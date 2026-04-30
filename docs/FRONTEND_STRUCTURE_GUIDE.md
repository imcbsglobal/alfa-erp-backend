# Alfa Agencies Frontend Structure Guide

**Date:** April 22, 2026  
**Framework:** React + Vite + Tailwind CSS  
**Base URL:** `e:\IMC PROJECT\Alfa_Agencies\alfa_agencies_frontend`

---

## 1. TABLE COMPONENT PATTERNS

### Pattern: Standard Data Table with Sorting, Pagination & Filtering

**Location:** [src/features/invoice/pages/InvoiceListPage.jsx](src/features/invoice/pages/InvoiceListPage.jsx)

#### Table Structure:
```jsx
<div className="bg-white rounded-xl shadow overflow-hidden">
  <div className="overflow-x-auto">
    <table className="w-full">
      <thead className="bg-gradient-to-r from-teal-500 to-cyan-600 text-white">
        <tr>
          <th className="px-4 py-3 text-left">Invoice</th>
          <th className="px-4 py-3 text-left">Priority</th>
          <th className="px-4 py-3 text-left">Date</th>
          <th className="px-4 py-3 text-left">Customer</th>
          <th className="px-4 py-3 text-left">Created By</th>
          <th className="px-4 py-3 text-right">Amount</th>
          <th className="px-4 py-3 text-center">Status</th>
          <th className="px-4 py-3 text-left">Actions</th>
        </tr>
      </thead>
      <tbody className="divide-y">
        {currentItems.map((inv) => (
          <tr key={inv.id} className="transition hover:bg-gray-50">
            <td className="px-4 py-3">{/* row data */}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
</div>
```

#### Sorting Implementation:
```jsx
// Sort invoices: HIGH priority first, then by creation date
const sortedInvoices = [...invoices].sort((a, b) => {
  if (a.priority === 'HIGH' && b.priority !== 'HIGH') return -1;
  if (a.priority !== 'HIGH' && b.priority === 'HIGH') return 1;
  return new Date(a.created_at) - new Date(b.created_at);
});
```

#### Filtering Implementation:
```jsx
const filteredInvoices = sortedInvoices.filter(inv => {
  if (!searchTerm.trim()) return true;
  const search = searchTerm.toLowerCase();
  return (
    inv.invoice_no?.toLowerCase().includes(search) ||
    inv.customer?.name?.toLowerCase().includes(search) ||
    inv.customer?.code?.toLowerCase().includes(search)
  );
});
```

#### Pagination:
```jsx
const indexOfLastItem = currentPage * itemsPerPage;
const indexOfFirstItem = indexOfLastItem - itemsPerPage;
const currentItems = filteredInvoices.slice(indexOfFirstItem, indexOfLastItem);
```

### Key Features:
- **Responsive:** `overflow-x-auto` wrapper for mobile scrolling
- **Hover Effects:** `hover:bg-gray-50` on table rows
- **Alternating Rows:** `divide-y` class for row separation
- **Status Badges:** Priority and status columns use color-coded badges
- **Actions Column:** Contains buttons (Pick, View, Edit, etc.)

### Badge Color Functions:
```jsx
// Priority badges
const getPriorityBadgeColor = (priority) => {
  switch (priority) {
    case "HIGH": return "bg-red-100 text-red-700 border-red-300";
    case "MEDIUM": return "bg-yellow-100 text-yellow-700 border-yellow-300";
    case "LOW": return "bg-gray-100 text-gray-600 border-gray-300";
  }
};

// Status badges (from invoiceStatus.js)
export const INVOICE_STATUS_COLORS = {
  INVOICED:   "bg-yellow-100 text-yellow-700 border-yellow-300",
  PICKING:    "bg-blue-100 text-blue-700 border-blue-300",
  PICKED:     "bg-green-100 text-green-700 border-green-300",
  PACKING:    "bg-purple-100 text-purple-700 border-purple-300",
  BOXING:     "bg-orange-100 text-orange-700 border-orange-300",
  PACKED:     "bg-emerald-100 text-emerald-700 border-emerald-300",
  DISPATCHED: "bg-teal-100 text-teal-700 border-teal-300",
  DELIVERED:  "bg-gray-200 text-gray-700 border-gray-300",
  REVIEW:     "bg-red-100 text-red-700 border-red-300",
};
```

### Reusable Pagination Component:

**Location:** [src/components/Pagination.jsx](src/components/Pagination.jsx)

```jsx
<Pagination
  currentPage={currentPage}
  totalItems={filteredInvoices.length}
  itemsPerPage={itemsPerPage}
  onPageChange={handlePageChange}
  label="records"
  colorScheme="teal" // "teal" or "orange"
/>
```

**Features:**
- Smart page numbering (max 5 visible pages)
- Ellipsis for skipped pages
- Prev/Next buttons with disabled states
- Row count display: "Showing X to Y of Z records"
- Supports two color schemes: teal (default) and orange

---

## 2. MODAL/SIDE PANEL STRUCTURE

### Pattern: Detail Modal (InvoiceDetailModal)

**Location:** [src/components/InvoiceDetailModal.jsx](src/components/InvoiceDetailModal.jsx)

#### Basic Structure:
```jsx
if (!isOpen) return null;

return (
  <div 
    className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 p-2 sm:p-4"
    onClick={onClose}
    style={{ zIndex: 10000 }}
  >
    <div 
      className="bg-white rounded-lg shadow-2xl w-full max-w-6xl max-h-[95vh] sm:max-h-[90vh] overflow-hidden flex flex-col relative"
      onClick={(e) => e.stopPropagation()}
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-teal-500 to-cyan-600 text-white px-3 py-3 sm:px-6 sm:py-4 flex justify-between items-center">
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Icon in header background */}
          <div className="bg-white bg-opacity-20 p-1.5 sm:p-2 rounded">
            <svg className="w-4 h-4 sm:w-5 sm:h-5">...</svg>
          </div>
          <h2 className="text-base sm:text-xl font-bold">Invoice Details</h2>
        </div>
        <button onClick={onClose} className="hover:bg-white hover:bg-opacity-20 rounded p-1">
          <X className="w-5 h-5 sm:w-6 sm:h-6" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto bg-gray-50">
        {loading ? (
          <div className="text-center py-12 text-gray-500">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-teal-500 mx-auto"></div>
            <p className="mt-4">Loading...</p>
          </div>
        ) : (
          // Content here
        )}
      </div>
    </div>
  </div>
);
```

#### Modal Features:
- **Fixed Overlay:** `fixed inset-0` with semi-transparent dark backdrop
- **Responsive Sizing:** `w-full max-w-6xl` for fluid width, max-height responsive
- **Header Gradient:** `bg-gradient-to-r from-teal-500 to-cyan-600` (signature pattern)
- **Close Button:** X icon in top-right with hover effect
- **Scrollable Content:** Content area with `overflow-y-auto`
- **Loading State:** Spinner with animated rotation

### Pattern: Confirmation Modal (ConfirmationModal)

**Location:** [src/components/ConfirmationModal.jsx](src/components/ConfirmationModal.jsx)

```jsx
export default function ConfirmationModal({
  isOpen,
  onClose,
  onConfirm,
  title = "Confirm Action",
  message,
  confirmText = "OK",
  cancelText = "Cancel",
  confirmButtonClass = "bg-red-600 hover:bg-red-700 text-white"
})
```

#### Structure:
- **Header:** Border-bottom, bold title
- **Body:** Whitespace-pre-line for formatted text
- **Footer:** Left-aligned cancel, right-aligned confirm
- **Customizable:** Title, message, button text, button colors

### Modal Z-index Stack:
- Profile menu: `zIndex: 950`
- Modal overlay: `zIndex: 10000`
- Ensures proper layering across the app

### Table Within Modal:

```jsx
<div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
  <div className="overflow-x-auto">
    <table className="w-full min-w-[800px]">
      <thead>
        <tr className="bg-gradient-to-r from-teal-500 to-cyan-600 text-white">
          <th className="px-3 sm:px-4 py-2 sm:py-3 text-left text-xs font-bold uppercase tracking-wide">
            Column Name
          </th>
        </tr>
      </thead>
      <tbody className="bg-white">
        {items?.map((item, idx) => (
          <tr key={idx} className="border-b border-gray-200 hover:bg-gray-50">
            <td className="px-3 sm:px-4 py-2 sm:py-3 text-xs sm:text-sm">{item.value}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
  {/* Total section */}
  <div className="bg-gray-50 border-t border-gray-200 px-3 sm:px-4 py-3 flex justify-end">
    <div className="text-right">
      <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Total</p>
      <p className="text-xl sm:text-2xl font-bold text-teal-600">₹ Value</p>
    </div>
  </div>
</div>
```

---

## 3. TAILWIND CSS & STYLING PATTERNS

### Color Theme

#### Teal Theme (Primary):
- **Header/Primary:** `bg-gradient-to-r from-teal-500 to-cyan-600`
- **Hover gradient:** `hover:from-teal-600 hover:to-cyan-700`
- **Text:** `text-teal-600` for emphasis
- **Light backgrounds:** `bg-teal-50`, `bg-teal-100`
- **Rings:** `ring-2 ring-teal-100` (for borders)

#### Orange Theme (Secondary/Billing):
- **Header:** `bg-gradient-to-r from-orange-500 to-red-600`
- **Hover:** `hover:from-orange-600 hover:to-red-700`
- **Text:** `text-orange-600`, `text-red-600`
- **Light backgrounds:** `bg-orange-50`, `bg-orange-100`

#### Neutral Colors:
- **Backgrounds:** `bg-white`, `bg-gray-50`, `bg-gray-100`
- **Text:** `text-gray-800` (dark), `text-gray-500` (medium), `text-gray-400` (light)
- **Borders:** `border-gray-200`, `border-gray-300`

#### Semantic Status Colors:
- **HIGH Priority:** `bg-red-100 text-red-700 border-red-300`
- **MEDIUM Priority:** `bg-yellow-100 text-yellow-700 border-yellow-300`
- **LOW Priority:** `bg-gray-100 text-gray-600 border-gray-300`

### Common Style Classes

#### Buttons:
```jsx
// Primary Teal Button
className="px-4 py-2 bg-gradient-to-r from-teal-500 to-cyan-600 text-white rounded-lg font-semibold shadow-lg hover:from-teal-600 hover:to-cyan-700 transition-all"

// Secondary Button
className="px-6 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors"

// Danger Button
className="bg-red-600 hover:bg-red-700 text-white"
```

#### Cards:
```jsx
className="bg-white rounded-lg shadow-sm border border-gray-200"
className="bg-white rounded-xl shadow overflow-hidden"
```

#### Input Fields:
```jsx
className="px-4 pr-10 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 w-full text-sm"
```

#### Badges:
```jsx
// Template
className={`px-3 py-1 rounded-full border text-xs font-bold ${getPriorityBadgeColor(priority)}`}
```

#### Responsive Spacing:
- **Padding:** `p-3 sm:p-6` (mobile-first, larger on desktop)
- **Gap:** `gap-3` or `gap-4`
- **Text Size:** `text-xs sm:text-sm`, `text-base sm:text-xl`
- **Width:** `w-full sm:w-64`, `w-14 h-14`

#### Header Typography:
- **Page Title:** `text-2xl font-bold text-gray-800`
- **Section Heading:** `text-base sm:text-xl font-bold`
- **Column Headers:** `text-xs font-bold uppercase tracking-wide`

### Hover & Transition Effects:
```jsx
className="transition hover:bg-gray-50"
className="transition-all"
className="transition-transform"  // For rotating icons
className="transition-colors"
```

### Responsive Design:
- **Breakpoint:** `sm:` (640px), `lg:` (1024px)
- **Stack Layout:** `flex-col lg:flex-row`
- **Hide/Show:** `hidden sm:block`, `lg:hidden`

### Custom CSS Classes:
```css
/* In index.css */
.hide-scrollbar::-webkit-scrollbar { display: none; }
.hide-scrollbar { scrollbar-width: none; -ms-overflow-style: none; }
```

---

## 4. TOPBAR STRUCTURE (MainLayout)

**Location:** [src/layout/MainLayout.jsx](src/layout/MainLayout.jsx)

### Layout Structure:
```jsx
<div className="h-screen bg-gray-50 flex overflow-hidden">
  {/* Sidebar - Fixed width 16rem (open) or 5rem (closed) */}
  <Sidebar {...props} />

  {/* Main Content Area */}
  <main className="flex-1 bg-gray-50 transition-all duration-300 w-full">
    {/* Fixed Topbar */}
    <header className="h-14 sm:h-16 bg-white border-b border-gray-200 flex items-center justify-between px-3 sm:px-6 shadow-sm" />

    {/* Page Content */}
    <div className="pt-16 sm:pt-20 p-3 sm:p-6 h-full overflow-y-auto">
      <Outlet />
    </div>
  </main>
</div>
```

### Topbar Features:

#### Left Section - Menu Toggle:
```jsx
<button
  onClick={() => setSidebarOpen(!sidebarOpen)}
  className="lg:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
  aria-label="Toggle Menu"
>
  <MenuIcon className="w-6 h-6 text-gray-600" />
</button>
```

#### Right Section - Profile Menu:
```jsx
<div className="relative" data-profile-menu style={{ zIndex: 950 }}>
  <button
    data-profile-button
    onClick={() => setShowProfileMenu(!showProfileMenu)}
    className="flex items-center gap-2 sm:gap-3 px-2 sm:px-3 py-2 rounded-lg hover:bg-gray-50 transition-all"
  >
    {/* User Info - Hidden on Mobile */}
    <div className="text-right hidden sm:block">
      <p className="font-semibold text-gray-800 text-sm">{user?.name}</p>
      <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
    </div>

    {/* Avatar Circle */}
    <div className="w-14 h-14 rounded-full bg-gradient-to-br from-teal-400 to-cyan-500 flex items-center justify-center text-white font-bold shadow-md ring-2 ring-teal-100">
      {user?.avatar ? (
        <img src={user.avatar} alt={user.name} className="w-full h-full object-cover" />
      ) : (
        <span>{user?.name?.charAt(0)}</span>
      )}
    </div>

    {/* Chevron Down (rotates when menu open) */}
    <ChevronDownIcon
      className={`w-3 h-3 sm:w-4 sm:h-4 text-gray-600 transition-transform ${
        showProfileMenu ? "rotate-180" : ""
      }`}
    />
  </button>

  {/* Dropdown Menu */}
  {showProfileMenu && (
    <div className="absolute right-0 top-full mt-2 w-56 sm:w-64 bg-white border border-gray-200 shadow-xl rounded-lg py-2">
      <div className="px-4 py-3 border-b border-gray-100">
        <p className="font-semibold text-gray-800 text-sm">{user?.name}</p>
        <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
      </div>
      <button
        onClick={handleLogout}
        className="w-full px-4 py-2.5 text-left text-sm text-red-600 hover:bg-red-50 flex items-center gap-3"
      >
        <LogoutIcon className="w-4 h-4" />
        Logout
      </button>
    </div>
  )}
</div>
```

### Topbar Styling:
- **Fixed Positioning:** Adjusts based on sidebar state
- **Height:** `h-14 sm:h-16` (56px mobile, 64px desktop)
- **Shadow:** `shadow-sm` for subtle depth
- **Z-index:** `zIndex: 30` to stay above content
- **Responsive:** Padding adjusts `px-3 sm:px-6`
- **Avatar:** Gradient background, shadow ring, responsive sizing

### How to Add Icons/Badges to Topbar:

**Add Notification Badge Example:**
```jsx
<div className="relative">
  <button className="p-2 hover:bg-gray-100 rounded-lg">
    <BellIcon className="w-5 h-5 text-gray-600" />
  </button>
  {/* Badge */}
  <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
</div>
```

**Add Search in Topbar:**
```jsx
<div className="hidden sm:flex items-center gap-3 flex-1 max-w-sm mx-4">
  <input
    type="text"
    placeholder="Search..."
    className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 text-sm w-full"
  />
</div>
```

---

## 5. AVAILABLE FORMATTERS

**Location:** [src/utils/formatters.js](src/utils/formatters.js)

### Number Formatting:

```javascript
// Fixed decimal places
formatNumber(value, decimals = 2, fallback = "0.00")
// Example: formatNumber(123.456, 2) → "123.46"

// Currency with rupee symbol
formatCurrency(value, decimals = 2)
// Example: formatCurrency(500) → "₹500.00"

// Thousands separator (Indian locale)
formatNumberWithSeparator(value)
// Example: formatNumberWithSeparator(100000) → "1,00,000"

// File size in KB
formatFileSize(sizeInBytes, decimals = 1)
// Example: formatFileSize(2048) → "2.0 KB"

// Geographic coordinates
formatCoordinate(coordinate, decimals = 6)
// Example: formatCoordinate(28.7041) → "28.704100"
```

### Date Formatting:

```javascript
// Simple date (D/M/YYYY)
formatDate(dateValue, locale = 'en-IN', options = {})
// Example: formatDate("2026-04-22") → "22/4/2026"

// Date with DD/MM/YYYY format
formatDateDDMMYYYY(dateValue)
// Example: formatDateDDMMYYYY("2026-04-22") → "22/04/2026"

// Date with MM/DD/YYYY format
formatDateMMDDYYYY(dateValue)
// Example: formatDateMMDDYYYY("2026-04-22") → "04/22/2026"

// Date with month name
formatDateWithMonthName(dateValue, locale = 'en-IN')
// Example: formatDateWithMonthName("2026-04-22") → "22 April 2026"

// Invoice date format
formatInvoiceDate(dateValue)
// Example: formatInvoiceDate("2026-04-22") → "22/04/2026"

// Detailed date (weekday, month name)
formatDetailedDate(dateValue, locale = 'en-IN')
// Example: formatDetailedDate("2026-04-22") → "Wed, Apr 22, 2026"

// Time only (HH:MM:SS am/pm)
formatTime(dateValue, locale = 'en-IN')
// Example: formatTime("2026-04-22T14:30:45") → "2:30:45 pm"

// Date and time
formatDateTime(dateValue, locale = 'en-IN', options = {})
// Example: formatDateTime("2026-04-22T14:30:45") → "4/22/2026, 2:30:45 PM"

// Detailed date-time
formatDetailedDateTime(dateValue, locale = 'en-US')
// Example: formatDetailedDateTime("2026-04-22T14:30:45") → "Apr 22, 2026, 02:30 PM"

// Get today's ISO string (YYYY-MM-DD)
getTodayISOString()
// Example: getTodayISOString() → "2026-04-22"

// Duration between dates or minutes
formatDuration(value, endTime)
// Example: formatDuration(90) → "1h 30m"
```

### Domain-Specific Formatters:

These are used in features like billing, picking, etc.:

```javascript
// These are typically defined in feature services or components
formatMRP(value)              // MRP (Maximum Retail Price)
formatQuantity(qty, unit)     // Quantity with unit (e.g., "5 pcs")
formatAmount(value)           // Amount display format
formatLineTotal(qty, price)   // Item line total
formatInvoiceNo(no)           // Invoice number format
```

### Usage Example in Component:

```jsx
import {
  formatNumber,
  formatDate,
  formatCurrency,
  formatTime,
  formatDateDDMMYYYY
} from '../utils/formatters';

export default function InvoiceRow({ invoice }) {
  return (
    <tr>
      <td>{invoice.invoice_no}</td>
      <td>{formatDateDDMMYYYY(invoice.invoice_date)}</td>
      <td>{formatTime(invoice.created_at)}</td>
      <td className="text-right font-semibold">
        {formatCurrency(invoice.Total)}
      </td>
      <td>{formatNumber(invoice.quantity, 0)}</td>
    </tr>
  );
}
```

---

## 6. UTILITY HOOKS & HELPERS

### useUrlPage Hook

**Location:** [src/utils/useUrlPage.js](src/utils/useUrlPage.js)

Syncs pagination with URL query parameters for browser back/forward navigation.

```jsx
const [currentPage, setCurrentPage] = useUrlPage('page');
// URL changes: ?page=1, ?page=2, etc.
// Preserves page on browser navigation
```

### usePersistedFilters Hook

**Location:** [src/utils/usePersistedFilters.js](src/utils/usePersistedFilters.js)

Persists filter state to localStorage.

```jsx
const [filters, saveFilters, clearFilters] = usePersistedFilters('invoiceFilters', {
  status: 'ALL',
  priority: 'ALL'
});

// Save filters
saveFilters({ status: 'INVOICED', priority: 'HIGH' });

// Clear filters
clearFilters();
```

### Status Color Helpers

**Location:** [src/utils/invoiceStatus.js](src/utils/invoiceStatus.js)

```javascript
// Get Tailwind classes for status badge
getInvoiceStatusColor(status)  // Returns className string
// Example: getInvoiceStatusColor('PICKING') → "bg-blue-100 text-blue-700 border-blue-300"

// Get user-friendly label
getInvoiceStatusLabel(status)  // Returns display label
// Example: getInvoiceStatusLabel('BOXING') → "IN PROGRESS"

// Predefined color map
INVOICE_STATUS_COLORS = {
  INVOICED:   "bg-yellow-100 text-yellow-700 border-yellow-300",
  PICKING:    "bg-blue-100 text-blue-700 border-blue-300",
  PICKED:     "bg-green-100 text-green-700 border-green-300",
  PACKING:    "bg-purple-100 text-purple-700 border-purple-300",
  BOXING:     "bg-orange-100 text-orange-700 border-orange-300",
  PACKED:     "bg-emerald-100 text-emerald-700 border-emerald-300",
  DISPATCHED: "bg-teal-100 text-teal-700 border-teal-300",
  DELIVERED:  "bg-gray-200 text-gray-700 border-gray-300",
  REVIEW:     "bg-red-100 text-red-700 border-red-300",
}
```

---

## 7. KEY COMPONENT PATTERNS

### Icon System

**Location:** [src/layout/Icons.jsx](src/layout/Icons.jsx)

Custom SVG icon exports + Lucide React icons imported in MainLayout.

```jsx
// Custom SVG Icons
export const HomeIcon = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    {/* SVG path */}
  </svg>
);

// Usage
import { HomeIcon, ChevronDownIcon } from './layout/Icons';

<HomeIcon className="w-5 h-5 text-gray-600" />
```

### ToastProvider Component

**Location:** [src/components/ToastProvider.jsx](src/components/ToastProvider.jsx)

Global toast notifications using react-hot-toast.

```jsx
import toast from 'react-hot-toast';

toast.success('Picking completed!');
toast.error('Failed to load invoices', { duration: 6000 });
toast.info('Completion cancelled');
```

### Sidebar Navigation

**Location:** [src/layout/Sidebar/Sidebar.jsx](src/layout/Sidebar/Sidebar.jsx)

Collapsible sidebar with menu config from backend or frontend.

---

## 8. RESPONSIVE DESIGN PATTERNS

### Mobile-First Approach:

```jsx
// Base classes apply to mobile, sm: and lg: override for larger screens

// Text sizes
className="text-xs sm:text-sm lg:text-base"

// Padding/spacing
className="p-3 sm:p-4 lg:p-6"
className="px-4 py-2 sm:px-6 sm:py-3"

// Layout direction
className="flex flex-col sm:flex-row lg:gap-4"

// Visibility
className="hidden sm:block"  // Show on sm and larger
className="lg:hidden"        // Hide on lg and larger

// Sizing
className="w-full sm:w-64 lg:w-96"

// Tables
<div className="overflow-x-auto">  {/* Mobile scrollable */}
  <table className="w-full min-w-[800px]">  {/* Minimum width on mobile */}
```

### Responsive Tables:

Tables use `overflow-x-auto` wrapper to handle mobile without breaking layout.

```jsx
<div className="overflow-x-auto">
  <table className="w-full">  {/* w-full fills container */}
    {/* Responsive text sizes */}
    <th className="px-3 sm:px-4 py-2 sm:py-3 text-xs sm:text-sm">
```

---

## 9. COMMON WORKFLOW

### Creating a New Feature Table Page:

1. **Component Structure:**
   ```jsx
   // State management
   const [data, setData] = useState([]);
   const [searchTerm, setSearchTerm] = useState('');
   const [currentPage, setCurrentPage] = useUrlPage('page');
   
   // Filtering
   const filtered = data.filter(/* ... */);
   
   // Sorting
   const sorted = [...filtered].sort(/* ... */);
   
   // Pagination
   const currentItems = sorted.slice(start, end);
   
   // Render
   return (
     <div className="min-h-screen bg-gray-50 p-4">
       <div className="max-w-7xl mx-auto">
         {/* Header with search */}
         {/* Table */}
         {/* Pagination */}
       </div>
     </div>
   );
   ```

2. **Apply Consistent Styling:**
   - Use teal gradient for primary actions: `from-teal-500 to-cyan-600`
   - Use gray backgrounds: `bg-white`, `bg-gray-50`
   - Add shadows: `shadow` or `shadow-sm`

3. **Add Formatters:**
   - Import from `utils/formatters.js`
   - Use appropriate formatter for each data type

4. **Handle Loading/Error States:**
   - Spinner for loading
   - Error message display
   - Empty state message

---

## 10. FILE STRUCTURE SUMMARY

```
src/
├── components/              # Reusable components
│   ├── Pagination.jsx       # Table pagination (teal/orange themes)
│   ├── ConfirmationModal.jsx
│   ├── InvoiceDetailModal.jsx
│   ├── ToastProvider.jsx    # Global notifications
│   └── ...
├── layout/                  # Layout components
│   ├── MainLayout.jsx       # Main app layout + topbar
│   ├── Icons.jsx            # Custom SVG icons
│   └── Sidebar/             # Navigation sidebar
├── features/                # Feature modules (invoice, billing, picking, etc.)
│   ├── invoice/
│   │   ├── pages/           # Page components (list, view, edit)
│   │   └── components/      # Feature-specific components
│   ├── billing/
│   └── ...
├── utils/                   # Utility functions and hooks
│   ├── formatters.js        # Formatting utilities
│   ├── invoiceStatus.js     # Status color/label helpers
│   ├── useUrlPage.js        # Pagination hook
│   ├── usePersistedFilters.js
│   └── ...
├── services/                # API service layer
├── App.jsx
├── index.css                # Tailwind imports
└── main.jsx
```

---

## 11. STYLING QUICK REFERENCE

| Element | Class Pattern |
|---------|---------------|
| **Page Background** | `bg-gray-50` |
| **Card/Container** | `bg-white rounded-lg shadow` |
| **Primary Button** | `bg-gradient-to-r from-teal-500 to-cyan-600 hover:from-teal-600 hover:to-cyan-700 text-white` |
| **Secondary Button** | `border border-gray-300 text-gray-700 hover:bg-gray-50` |
| **Table Header** | `bg-gradient-to-r from-teal-500 to-cyan-600 text-white` |
| **Status Badge** | `px-3 py-1 rounded-full border text-xs font-bold [color-class]` |
| **Priority Badge** | HIGH: red-100/700, MEDIUM: yellow-100/700, LOW: gray-100/600 |
| **Avatar Circle** | `rounded-full bg-gradient-to-br from-teal-400 to-cyan-500 ring-2 ring-teal-100` |
| **Input Field** | `border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500` |
| **Modal Overlay** | `fixed inset-0 bg-black bg-opacity-50` |

---

**Last Updated:** April 22, 2026  
**Status:** Complete frontend exploration and documentation
