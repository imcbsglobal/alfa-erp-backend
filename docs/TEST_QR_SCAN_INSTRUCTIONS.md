# QR Code Box Scanning - Testing Instructions

## Important Note about Box Database

The box you scanned (`BOX-0002-001-017877`) doesn't exist in the database yet because:

1. **Box labels are printed BEFORE packing is completed**
2. **Boxes are saved to database ONLY when you click "Mark as PACKED"**

## Current Status

Your database currently has: **1 box**
- Box ID: `BOX-0001-001-704783`

## How to Test the QR Scanning Feature

### Option 1: Complete the Packing First
1. Go to the packing page where you have `BOX-0002-001-017877`
2. Complete assigning all items to boxes
3. Click **"Mark as PACKED & Ready"** button
4. Now scan the QR code - it will work!

### Option 2: Test with Existing Box
1. Visit this URL in your browser or scan a QR code that points to it:
   ```
   http://localhost:5173/box/BOX-0001-001-704783
   ```

## Workflow Summary

```
1. Assign items to boxes
   ↓
2. Complete box (enables label printing)
   ↓
3. Print QR label
   ↓
4. Click "Mark as PACKED" (saves boxes to database)
   ↓
5. NOW QR codes will work when scanned
```

## Testing the Endpoint Directly

### Backend API Test:
```bash
curl http://127.0.0.1:8000/api/sales/packing/box-details/BOX-0001-001-704783/
```

### Frontend URL:
```
http://localhost:5173/box/BOX-0001-001-704783
```

## Expected Result After Scanning

You should see:
- ✅ Box number
- ✅ Customer name and address
- ✅ Phone number
- ✅ All items in the box (name, code, quantity, batch, expiry, MRP)
- ✅ Related invoice numbers
- ✅ Packing date

## Troubleshooting

### If you get 404 error:
- The box hasn't been saved to database yet
- Complete the packing by clicking "Mark as PACKED"

### If you get other errors:
- Check if Django backend is running on port 8000
- Check if frontend is running on port 5173
- Check browser console for detailed error messages
