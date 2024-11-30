# Frontend Screens

## 1. Home Page

### Home Page Layout

```ascii
+------------------+
|     Header       |
+------------------+
|   Quick Stats    |
+------------------+
|  Action Cards    |
+------------------+
|     Footer      |
+------------------+
```

### Home Page Components

- Navigation bar with logo
- Quick statistics dashboard
- Action cards for main features
- Footer with links and info

## 2. Price Prediction Page

### Price Prediction Layout

```ascii
+------------------+
|    Car Input    |
+------------------+
|    Features     |
+------------------+
| Prediction View |
+------------------+
```

### Price Prediction Components

- Car details form
  - Make (dropdown)
  - Model (dependent dropdown)
  - Year (slider)
  - Mileage (input)
  - Fuel type (radio)
  - Transmission (radio)
  - Engine size (input)

- Prediction display
  - Estimated price
  - Confidence interval
  - Price range visualization
  - Similar cars comparison

## 3. Data Explorer

### Data Explorer Layout

```ascii
+------------------+
|    Filters      |
+------------------+
|   Data Grid     |
+------------------+
| Visualizations  |
+------------------+
```

### Data Explorer Components

- Filter panel
  - Search box
  - Price range
  - Year range
  - Make/Model filters
  - Feature filters

- Data grid
  - Sortable columns
  - Pagination
  - Export options
  - Row details

- Visualizations
  - Price distribution
  - Feature correlations
  - Trend analysis
  - Market insights

## 4. Model Analytics

### Analytics Layout

```ascii
+------------------+
| Model Overview  |
+------------------+
|  Performance    |
+------------------+
|    Insights     |
+------------------+
```

### Analytics Components

- Model metrics
  - Accuracy scores
  - Error rates
  - Training history
  - Version info

- Performance charts
  - Prediction vs actual
  - Error distribution
  - Feature importance
  - Residual plots

## 5. Settings Page

### Settings Layout

```ascii
+------------------+
|  User Settings  |
+------------------+
| App Settings    |
+------------------+
| System Info     |
+------------------+
```

### Settings Components

- User preferences
  - Theme selection
  - Display options
  - Notification settings
  - Default values

- Application settings
  - Cache management
  - Data refresh rate
  - Export settings
  - API configuration

## Style Guide

### Colors

```css
/* Primary Colors */
--primary: #2563eb;
--secondary: #7c3aed;
--accent: #059669;

/* Background Colors */
--bg-primary: #ffffff;
--bg-secondary: #f3f4f6;
--bg-accent: #e5e7eb;

/* Text Colors */
--text-primary: #111827;
--text-secondary: #4b5563;
--text-accent: #6b7280;
```

### Typography

```css
/* Fonts */
--font-primary: 'Inter', sans-serif;
--font-secondary: 'SF Pro Display', sans-serif;

/* Sizes */
--text-xs: 0.75rem;
--text-sm: 0.875rem;
--text-base: 1rem;
--text-lg: 1.125rem;
--text-xl: 1.25rem;
```

### Buttons

```css
.button-primary {
    background: var(--primary);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 0.375rem;
}

.button-secondary {
    background: var(--secondary);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 0.375rem;
}
```

### Cards

```css
.card {
    background: var(--bg-primary);
    border-radius: 0.5rem;
    padding: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
```

## Responsive Design

### Breakpoints

```css
/* Mobile */
@media (max-width: 640px) {
    /* Mobile styles */
}

/* Tablet */
@media (min-width: 641px) and (max-width: 1024px) {
    /* Tablet styles */
}

/* Desktop */
@media (min-width: 1025px) {
    /* Desktop styles */
}
```

### Layout Adjustments

- Mobile: Single column layout
- Tablet: Two column layout
- Desktop: Multi-column layout

### Transitions

```css
.transition-base {
    transition: all 0.3s ease;
}

.transition-smooth {
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
```

### Loading States

- Skeleton loading for data
- Spinner for actions
- Progress bars for processes
- Smooth transitions
