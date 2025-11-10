"""
Database connection pooling and batch operations for Firestore.
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

try:
    from google.cloud import firestore
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False

logger = logging.getLogger(__name__)


class DatabasePool:
    """
    Optimized Firestore operations with connection pooling, batching, and caching.
    """

    def __init__(self, project_id: Optional[str] = None):
        """
        Initialize database pool.

        Args:
            project_id: GCP project ID (optional)
        """
        if not FIRESTORE_AVAILABLE:
            logger.warning("Firestore not available")
            self.client = None
            return

        try:
            if project_id:
                self.client = firestore.Client(project=project_id)
            else:
                self.client = firestore.Client()
            logger.info("Firestore client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {e}")
            self.client = None

        # Batch configuration
        self.max_batch_size = 500  # Firestore limit
        self.batch_delay = 0.05  # 50ms batching window

        # Operation queue for batching
        self._batch_queue: Dict[str, List] = defaultdict(list)
        self._batch_lock = asyncio.Lock()

        # Simple cache for recent reads
        self._cache: Dict[str, Dict] = {}
        self._cache_ttl = 300  # 5 minutes
        self._cache_timestamps: Dict[str, datetime] = {}

    async def get_document(
        self,
        collection: str,
        document_id: str,
        use_cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Get a single document with caching.

        Args:
            collection: Collection name
            document_id: Document ID
            use_cache: Whether to use cache

        Returns:
            Document data or None if not found
        """
        if not self.client:
            logger.warning("Firestore client not available")
            return None

        cache_key = f"{collection}:{document_id}"

        # Check cache
        if use_cache and cache_key in self._cache:
            timestamp = self._cache_timestamps.get(cache_key)
            if timestamp and datetime.now() - timestamp < timedelta(seconds=self._cache_ttl):
                logger.debug(f"Cache hit: {cache_key}")
                return self._cache[cache_key]

        # Fetch from Firestore
        try:
            doc_ref = self.client.collection(collection).document(document_id)
            doc = doc_ref.get()

            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id

                # Update cache
                if use_cache:
                    self._cache[cache_key] = data
                    self._cache_timestamps[cache_key] = datetime.now()

                return data
            return None

        except Exception as e:
            logger.error(f"Error fetching document {collection}/{document_id}: {e}")
            return None

    async def batch_get(
        self,
        collection: str,
        document_ids: List[str],
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Batch get documents (up to 500 at once).

        Args:
            collection: Collection name
            document_ids: List of document IDs
            use_cache: Whether to use cache

        Returns:
            List of document data dicts
        """
        if not self.client:
            logger.warning("Firestore client not available")
            return []

        results = []
        uncached_ids = []

        # Check cache first
        if use_cache:
            for doc_id in document_ids:
                cache_key = f"{collection}:{doc_id}"
                if cache_key in self._cache:
                    timestamp = self._cache_timestamps.get(cache_key)
                    if timestamp and datetime.now() - timestamp < timedelta(seconds=self._cache_ttl):
                        results.append(self._cache[cache_key])
                        continue
                uncached_ids.append(doc_id)
        else:
            uncached_ids = document_ids

        # Fetch uncached in batches
        if uncached_ids:
            for i in range(0, len(uncached_ids), self.max_batch_size):
                batch_ids = uncached_ids[i:i + self.max_batch_size]
                batch_results = await self._fetch_batch(collection, batch_ids)

                # Update cache
                if use_cache:
                    for doc in batch_results:
                        cache_key = f"{collection}:{doc['id']}"
                        self._cache[cache_key] = doc
                        self._cache_timestamps[cache_key] = datetime.now()

                results.extend(batch_results)

        return results

    async def _fetch_batch(
        self,
        collection: str,
        document_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Internal method to fetch a batch of documents.

        Args:
            collection: Collection name
            document_ids: List of document IDs (max 500)

        Returns:
            List of document data dicts
        """
        try:
            # Create references
            doc_refs = [
                self.client.collection(collection).document(doc_id)
                for doc_id in document_ids
            ]

            # Fetch all at once
            docs = await asyncio.gather(*[
                asyncio.to_thread(doc_ref.get)
                for doc_ref in doc_refs
            ])

            # Convert to dicts
            results = []
            for doc in docs:
                if doc.exists:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    results.append(data)

            return results

        except Exception as e:
            logger.error(f"Error in batch fetch: {e}")
            return []

    async def batch_write(
        self,
        collection: str,
        documents: List[Dict[str, Any]]
    ):
        """
        Batch write documents (up to 500 at once).

        Args:
            collection: Collection name
            documents: List of document dicts (must include 'id' field)
        """
        if not self.client:
            logger.warning("Firestore client not available")
            return

        try:
            # Split into batches
            for i in range(0, len(documents), self.max_batch_size):
                batch_docs = documents[i:i + self.max_batch_size]
                await self._write_batch(collection, batch_docs)

                # Invalidate cache
                for doc in batch_docs:
                    cache_key = f"{collection}:{doc['id']}"
                    if cache_key in self._cache:
                        del self._cache[cache_key]
                    if cache_key in self._cache_timestamps:
                        del self._cache_timestamps[cache_key]

        except Exception as e:
            logger.error(f"Error in batch write: {e}")

    async def _write_batch(
        self,
        collection: str,
        documents: List[Dict[str, Any]]
    ):
        """
        Internal method to write a batch of documents.

        Args:
            collection: Collection name
            documents: List of document dicts (max 500)
        """
        try:
            batch = self.client.batch()

            for doc in documents:
                doc_id = doc.pop('id', None)
                if not doc_id:
                    logger.warning("Document missing 'id' field, skipping")
                    continue

                doc_ref = self.client.collection(collection).document(doc_id)
                batch.set(doc_ref, doc, merge=True)

            # Commit batch
            await asyncio.to_thread(batch.commit)
            logger.debug(f"Batch wrote {len(documents)} documents to {collection}")

        except Exception as e:
            logger.error(f"Error writing batch: {e}")

    async def query_with_cache(
        self,
        collection: str,
        filters: List[tuple],
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        use_cache: bool = True,
        cache_ttl: int = 300
    ) -> List[Dict[str, Any]]:
        """
        Query documents with caching.

        Args:
            collection: Collection name
            filters: List of (field, operator, value) tuples
            order_by: Field to order by
            limit: Maximum number of results
            use_cache: Whether to use cache
            cache_ttl: Cache TTL in seconds

        Returns:
            List of matching documents
        """
        if not self.client:
            logger.warning("Firestore client not available")
            return []

        # Generate cache key
        filter_str = "|".join([f"{f[0]}{f[1]}{f[2]}" for f in filters])
        cache_key = f"query:{collection}:{filter_str}:{order_by}:{limit}"

        # Check cache
        if use_cache and cache_key in self._cache:
            timestamp = self._cache_timestamps.get(cache_key)
            if timestamp and datetime.now() - timestamp < timedelta(seconds=cache_ttl):
                logger.debug(f"Query cache hit: {cache_key}")
                return self._cache[cache_key]

        # Execute query
        try:
            query = self.client.collection(collection)

            # Apply filters
            for field, operator, value in filters:
                query = query.where(field, operator, value)

            # Apply ordering
            if order_by:
                query = query.order_by(order_by)

            # Apply limit
            if limit:
                query = query.limit(limit)

            # Execute
            docs = await asyncio.to_thread(query.get)

            # Convert to dicts
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)

            # Cache results
            if use_cache:
                self._cache[cache_key] = results
                self._cache_timestamps[cache_key] = datetime.now()

            return results

        except Exception as e:
            logger.error(f"Error in query: {e}")
            return []

    def clear_cache(self, pattern: Optional[str] = None):
        """
        Clear cache entries.

        Args:
            pattern: Optional pattern to match
        """
        if pattern:
            keys_to_delete = [
                k for k in self._cache.keys()
                if pattern in k
            ]
            for key in keys_to_delete:
                del self._cache[key]
                if key in self._cache_timestamps:
                    del self._cache_timestamps[key]
            logger.info(f"Cleared {len(keys_to_delete)} cache entries matching '{pattern}'")
        else:
            self._cache.clear()
            self._cache_timestamps.clear()
            logger.info("Cleared all cache entries")

    def get_stats(self) -> Dict[str, Any]:
        """Get database pool statistics."""
        return {
            "cache_size": len(self._cache),
            "cache_ttl": self._cache_ttl,
            "max_batch_size": self.max_batch_size,
            "client_available": self.client is not None
        }
