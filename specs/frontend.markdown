# Frontend Specifications for ReactorSync

## Visual Hierarchy and Layout
- **Primary Dashboard**: Top-level navigation toggle (Card/Table/Map views). Hero section with reactor overview; search/filter bar.
  - **Card View**: Grid layout (responsive, 2-4 columns); each card: Reactor name, status badge (red/yellow/green circle), key metrics summary.
  - **Table View**: Full-width table with columns (Name, Status, Location, Health Score); sortable/filterable.
  - **Map View**: Full-screen React-Leaflet map; markers colored by status, popups with summaries.
- **Drill-Down Pages**: Modal or route-based; tabs for Telemetry (charts), Faults (list), Diagnostics (AI chat).
- **Admin Mode**: Toggle switch; panel with anomaly trigger buttons (e.g., dropdown per reactor).
- **Responsive Design**: Mobile-first; breakpoints at 600px, 1024px.

## Component Library
- **Core Components** (from ShadCN): Card, Table, Badge, ToggleGroup, Dialog, Tabs.
- **Custom Components**: 
  - **ReactorCard**: Displays name, status, mini-chart.
  - **TelemetryChart**: Plotly-based time series with zoom/annotations.
  - **AnomalyTrigger**: Admin dropdown for faults (e.g., "Temp Spike").
  - **AIChat**: Textarea with Command A responses.
- **Integration**: Use `npx shadcn-ui@latest add` to install components (e.g., `card`, `table`); customize via Tailwind CSS classes.

## Styleguide and Design Language
- **Theme**: Tailwind CSS (via ShadCN); primary color: #2563eb (blue for nuclear tech), error: #dc2626 (red), warning: #facc15 (yellow), success: #16a34a (green).
- **Typography**: Default system fonts (Inter via Tailwind); H1-H6 for hierarchy; body text 14px.
- **Spacing**: Tailwind spacing scale; 4px base unit (e.g., `p-4`, `m-4`).
- **Icons**: Lucide-react (included with ShadCN, e.g., AlertTriangle for warnings).
- **Design Principles**: Minimalist, data-dense; high contrast for alerts; dark mode supported via Tailwind.
- **Accessibility**: ARIA labels, keyboard nav; color contrast >4.5:1 (use Tailwind’s contrast utilities).

## Package Management
- **Yarn**: Manage dependencies with `yarn add` (e.g., `yarn add react-leaflet react-plotly.js`); lockfile: `yarn.lock`.
- **Setup**: Initialize with `yarn create next-app` (TypeScript template); add ShadCN via `npx shadcn-ui@latest init`.