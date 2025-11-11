"""
Input validation and sanitization for ConsultantOS
"""
from typing import List, Optional
import re
from consultantos.models import AnalysisRequest


class AnalysisRequestValidator:
    """Validator for analysis requests"""
    
    @staticmethod
    def validate_company(company: str) -> str:
        """
        Validate and sanitize company name
        
        Args:
            company: Company name to validate
        
        Returns:
            Sanitized company name
        
        Raises:
            ValueError: If company name is invalid
        """
        if not company:
            raise ValueError("Company name is required")
        
        # Strip whitespace first
        company = company.strip()
        
        # Sanitize before length checks
        company = re.sub(r'[<>"\']', '', company)
        
        # Check length after sanitization
        if not company or len(company) < 2:
            raise ValueError("Company name must be at least 2 characters after sanitization")
        
        if len(company) > 200:
            raise ValueError("Company name too long (max 200 characters)")
        
        return company
    
    @staticmethod
    def validate_industry(industry: Optional[str]) -> Optional[str]:
        """
        Validate industry name
        
        Args:
            industry: Industry name to validate
        
        Returns:
            Sanitized industry name or None
        """
        if not industry:
            return None
        
        industry = industry.strip()
        
        if len(industry) > 200:
            raise ValueError("Industry name too long (max 200 characters)")
        
        return industry
    
    @staticmethod
    def validate_frameworks(frameworks: List[str]) -> List[str]:
        """
        Validate framework selection
        
        Args:
            frameworks: List of framework names
        
        Returns:
            Validated and normalized framework list
        
        Raises:
            ValueError: If frameworks are invalid
        """
        if not frameworks:
            raise ValueError("At least one framework must be selected")
        
        valid_frameworks = {
            "porter", "swot", "pestel", "blue_ocean",
            "ansoff", "bcg_matrix", "value_chain"
        }
        normalized = [f.lower().strip() for f in frameworks]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_frameworks = []
        for f in normalized:
            if f not in seen:
                seen.add(f)
                unique_frameworks.append(f)
        
        invalid = set(unique_frameworks) - valid_frameworks
        if invalid:
            raise ValueError(
                f"Invalid frameworks: {invalid}. "
                f"Valid options: {', '.join(sorted(valid_frameworks))}"
            )
        
        return unique_frameworks
    
    @staticmethod
    def validate_depth(depth: Optional[str]) -> str:
        """
        Validate analysis depth
        
        Args:
            depth: Depth level
        
        Returns:
            Validated depth
        """
        valid_depths = {"quick", "standard", "deep"}
        
        if not depth:
            return "standard"
        
        depth = depth.lower().strip()
        
        if depth not in valid_depths:
            raise ValueError(
                f"Invalid depth: {depth}. "
                f"Valid options: {', '.join(valid_depths)}"
            )
        
        return depth
    
    @staticmethod
    def validate_request(request: AnalysisRequest) -> AnalysisRequest:
        """
        Validate complete analysis request
        
        Args:
            request: Analysis request to validate
        
        Returns:
            Validated request (may be modified)
        
        Raises:
            ValueError: If request is invalid
        """
        # Validate and update fields
        request.company = AnalysisRequestValidator.validate_company(request.company)
        request.industry = AnalysisRequestValidator.validate_industry(request.industry)
        request.frameworks = AnalysisRequestValidator.validate_frameworks(request.frameworks)
        request.depth = AnalysisRequestValidator.validate_depth(request.depth)
        
        return request

