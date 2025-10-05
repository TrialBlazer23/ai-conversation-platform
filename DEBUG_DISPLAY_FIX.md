# Display Fix - Debugging Guide

## Problem
Responses are showing only usage information (tokens/cost) but no actual content text is being displayed.

## Changes Made

### 1. Enhanced `displayMessage()` Function
**File:** `static/js/app.js`

Added:
- Console logging to see the full message object
- Safety check to ensure `message.content` exists before rendering
- Fallback to empty string if content is undefined

### 2. Enhanced `nextTurnNonStreaming()` Function  
**File:** `static/js/app.js`

Added:
- Console logging of the full API response
- Console logging of the message object specifically

### 3. Enhanced `nextTurnStreaming()` Function
**File:** `static/js/app.js`

Added:
- Console logging of each stream data chunk
- Console logging of accumulated content as it builds up

### 4. Enhanced `renderMarkdown()` Function
**File:** `static/js/app.js`

Added:
- Empty/undefined text check with warning
- Try-catch error handling
- Fallback to escaped plain text on error
- Console logging of rendered output

## How to Debug

### Step 1: Open Browser Developer Tools
1. Start your application
2. Open Chrome/Firefox/Edge DevTools (F12)
3. Go to the **Console** tab

### Step 2: Start a Conversation
1. Configure your API keys
2. Add at least one model
3. Enter an initial prompt
4. Start the conversation
5. Click "Next Turn" to generate a response

### Step 3: Check Console Output
Look for these debug messages in the console:

**For Non-Streaming:**
```javascript
API Response: {...}
Message object: {...}
Displaying message: {...}
Message content: "actual text content here"
Rendered markdown: "<p>actual text...</p>"
```

**For Streaming:**
```javascript
Stream data: {type: 'metadata', ...}
Stream data: {type: 'content', chunk: '...'}
Accumulated content: "growing text..."
Rendered markdown: "<p>...</p>"
```

### Step 4: Identify the Issue

Check which of these scenarios matches:

#### Scenario A: `message.content` is undefined
**Console shows:**
```
Message content: undefined
```
**Problem:** Backend is not sending content in the response
**Fix needed:** Check `app.py` line ~177 to ensure response includes content

#### Scenario B: `message.content` is empty string
**Console shows:**
```
Message content: ""
```
**Problem:** Provider is returning empty response
**Fix needed:** Check the AI provider (e.g., `google_provider.py`) 

#### Scenario C: Content exists but not rendering
**Console shows:**
```
Message content: "Hello, this is a response"
Rendered markdown: ""
```
**Problem:** Markdown parser failing
**Fix needed:** Check marked.js library loading

#### Scenario D: Content rendering but not displaying
**Console shows:**
```
Message content: "Hello, this is a response"  
Rendered markdown: "<p>Hello, this is a response</p>"
```
**Problem:** CSS issue hiding content or HTML structure problem
**Fix needed:** Check `static/css/style.css` for `.message-content` styling

## Common Fixes

### Fix 1: If Provider Returns Wrong Format
Check the provider's `generate_response()` method returns a string, not a dict.

### Fix 2: If Backend Returns Wrong Structure  
The API response should have this structure:
```json
{
  "status": "success",
  "message": {
    "role": "assistant",
    "content": "The actual response text",
    "model": "Model Name",
    "timestamp": "2025-10-04T...",
    "tokens_used": 150,
    "cost": 0.0001
  }
}
```

### Fix 3: If CSS is Hiding Content
Check that `.message-content` has proper display properties:
```css
.message-content {
  display: block;
  visibility: visible;
  opacity: 1;
}
```

## Next Steps

Once you run the app and check the console:
1. Note which scenario matches your issue
2. Share the console output
3. We can apply the appropriate fix

## Cleanup

Once the issue is fixed, you can remove the debug logging by:
1. Removing all `console.log()` statements added
2. Keeping the safety checks (null/undefined checks)
3. Keeping the error handling in `renderMarkdown()`
