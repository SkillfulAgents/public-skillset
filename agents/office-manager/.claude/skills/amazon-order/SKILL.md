---
name: Amazon Order
description: Order items from Amazon using browser automation. Use this when the user wants to buy/order/purchase something from Amazon.
version: 1.0.2
---

# Amazon Order Skill

Standard operating procedure for ordering items from Amazon using browser MCP tool.

## Preferences

- **Office Address**: see the "Office setup" section of `CLAUDE.md` (filled in during onboarding)
- **Default shipping**: Ship to the OFFICE address unless the user specifies otherwise
- **Avoid**: Amazon Fresh listings unless the team explicitly configured Amazon Fresh (prefer regular Amazon fulfillment)
- Prefer Prime / Fast Delivery
- Ok to order multiple of smaller quantity when user asks for larger quantity

## Workflow

### 1. Open Amazon
```
browser_open("https://www.amazon.com")
```

### 2. Search for Product
- Use the search box (typically `@e79` or find `searchbox "Search Amazon"`)
- Fill search term and press Enter
- Or navigate directly: `https://www.amazon.com/s?k=<search+terms>`

### 3. Select Product
- Review search results
- **IMPORTANT**: Check that the product is sold by Amazon.com, NOT Amazon Fresh
- Look for "Ships from Amazon.com" or Prime delivery options
- Click on desired product to view details

### 4. Check Product Page
Key elements to verify:
- Price
- Prime delivery availability
- "Ships from and sold by Amazon.com" (preferred)
- Delivery date estimate

### 5. Select Quantity
- Find quantity dropdown: `combobox "Quantity:"`
- Use `browser_select(ref, "4")` to select quantity
- Or click the dropdown and select option

### 6. Add to Cart
- Click "Add to cart" button
- Wait for confirmation overlay/page

### 7. Proceed to Checkout
- Click "Proceed to checkout" button
- This goes to the secure checkout page

### 8. Change Shipping Address (CRITICAL)
The account's default address may NOT be the office. **Always verify and change to the office address if needed.**

Steps:
1. Look for "Delivering to" section showing current address
2. Click "Change" link next to the address
3. In address selection:
   - Click "Show more addresses" if needed
   - Find the office address (from CLAUDE.md "Office setup")
   - Use: `browser_run("find text \"<office street>\" click")` to select it
4. Click "Deliver to this address" button

### 9. Select Delivery Speed
Available options vary by address. Select the FREE delivery option unless the user requests faster.

### 10. Review Order
Verify:
- Correct items and quantities
- Shipping address is the office address
- Delivery date
- Order total

### 11. Place Order
- **Always ask user for confirmation before clicking "Place your order"**
- Click "Place your order" button
- Wait for confirmation page showing "Order placed, thanks!"

## Common Element References

These refs can change between pages, always use `browser_snapshot()` to get current refs.

| Element | Typical Location |
|---------|------------------|
| Search box | `searchbox "Search Amazon"` |
| Add to cart | `button "Add to cart"` |
| Quantity dropdown | `combobox "Quantity:"` |
| Proceed to checkout | `button "Proceed to checkout"` |
| Change address | `link "Change delivery address"` |
| Place order | `button "Place your order"` |
| Deliver to this address | `button "Deliver to this address"` |

## Tips & Troubleshooting

### Large Snapshots
Amazon pages often exceed token limits. Use bash to search:
```bash
cat <snapshot_file> | jq -r '.[0].text' | grep -iE "pattern"
```

### Element Blocked Errors
If you get "Element is blocked by another element":
1. Press Escape: `browser_press("Escape")`
2. Scroll: `browser_scroll("up", 200)`
3. Take screenshot to see what's blocking
4. Try clicking again

### Finding Specific Text
Use browser_run to click by text content:
```
browser_run("find text \"<office street>\" click")
```

### Dropdown Selection
Use `browser_select(ref, value)` for `<select>` elements:
```
browser_select("@e154", "4")
```

## Example Order Flow

```python
# 1. Open Amazon
browser_open("https://www.amazon.com")

# 2. Search
browser_fill("@searchbox", "diet coke 12 pack")
browser_press("Enter")

# 3. Select product (get refs from snapshot)
browser_click("@productLink")

# 4. Set quantity
browser_select("@quantityDropdown", "4")

# 5. Add to cart
browser_click("@addToCart")

# 6. Checkout
browser_click("@proceedToCheckout")

# 7. Change address to office
browser_click("@changeAddress")
browser_click("@showMoreAddresses")
browser_run("find text \"<office street>\" click")
browser_click("@deliverToThisAddress")

# 8. Confirm with user, then place order
browser_click("@placeOrder")
```

## Order Confirmation Details to Capture

After placing order, note:
- Order confirmation message
- Estimated delivery date
- Order total
- Shipping address confirmation
