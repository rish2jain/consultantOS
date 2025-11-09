/**
 * Helper functions for finding buttons by text content
 */

/**
 * Find button by text content (case-insensitive partial match)
 */
async function findButtonByText(page, textOptions) {
  const options = Array.isArray(textOptions) ? textOptions : [textOptions];
  
  const handle = await page.evaluateHandle((opts) => {
    const buttons = Array.from(document.querySelectorAll('button'));
    return buttons.find(btn => {
      const btnText = btn.textContent.toLowerCase().trim();
      return opts.some(opt => btnText.includes(opt.toLowerCase()));
    }) || null;
  }, options);
  
  // Convert JSHandle to ElementHandle if possible
  const element = await handle.asElement();
  return element;
}

/**
 * Find button by type and optional text
 */
async function findButton(page, options = {}) {
  const { type, text } = options;
  
  // First try type selector
  if (type) {
    const button = await page.$(`button[type="${type}"]`);
    if (button) {
      if (!text) return button;
      
      // Verify text matches
      const buttonText = await page.evaluate(el => el.textContent.toLowerCase().trim(), button);
      const textArray = Array.isArray(text) ? text : [text];
      if (textArray.some(t => buttonText.includes(t.toLowerCase()))) {
        return button;
      }
    }
  }
  
  // Try text-based search
  if (text) {
    return await findButtonByText(page, text);
  }
  
  // Fallback to first submit button
  return await page.$('button[type="submit"]');
}

module.exports = {
  findButtonByText,
  findButton
};

