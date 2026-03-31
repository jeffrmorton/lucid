# Lucid Dashboard Design Research

Comprehensive research into EEG/BCI dashboard designs and 2026 React best practices for real-time scientific data visualization.

---

## 1. Commercial & Open-Source EEG Dashboard Designs

### 1.1 OpenBCI GUI (v5)

**URL**: https://docs.openbci.com/Software/OpenBCISoftware/GUIDocs/
**Source**: https://github.com/OpenBCI/OpenBCI_GUI (Processing/Java)

**Layout**: Multi-widget tiled layout with up to 6 customizable windows across 12 preset layout configurations. A "Layout" button in the upper-right corner lets users switch arrangements. Each widget pane has a dropdown in the upper-left corner to swap between available widgets.

**Color scheme**: Supports light and dark themes (toggle with `{` key). Dark theme uses a navy/charcoal background. Channel traces are color-coded with vibrant colors (8-color cycle), and these colors are consistent across the Time Series and FFT widgets -- the same channel color appears in both views.

**EEG trace display**: Time Series widget shows vertically stacked channels, each as a continuous scrolling waveform in its assigned color. Each graph represents voltage at one electrode over time. Channel labels appear to the left. Disabled channels show red borders; active channels show green borders in the Channel Select UI.

**Band powers / FFT**: FFT widget shows frequency-domain power for each channel as overlaid curves using the same channel color coding. Focus Widget (now deprecated in v5) previously showed band power ratios.

**Spectrogram**: Dual spectrogram widget allows two channels to be compared side-by-side as scrolling 2D heatmaps (time vs. frequency). Color gradient is configurable between log and linear scales. A thick color bar on the right shows the current gradient.

**Head Plot**: Thermal gradient (blue to red) topographic map. Deeper red = more activity. Contour lines connect regions of similar activity levels.

**Signal quality**: Cyton Signal Widget uses traffic-light indicators (green/yellow/red circles) for each channel. Green = good impedance, yellow = acceptable, red = poor fit.

**Navigation**: Top bar with board selection, start/stop controls, layout selector, and session management. No sidebar -- everything is in the multi-pane workspace.

**Key takeaway**: The OpenBCI GUI is the most feature-complete open-source reference. Its widget system with swappable panels and consistent channel color coding across views is a strong pattern to follow. However, its Processing/Java foundation looks dated compared to modern web UIs.

---

### 1.2 Muse App (Interaxon)

**URL**: https://choosemuse.com/pages/app

**Layout**: Mobile-first consumer app (iOS/Android). Minimalist design oriented toward non-technical users. Tab-based navigation ("Train" tab, formerly "Meditate"). Post-session results screen with simple graphs.

**Color scheme**: Soft teals (primary brand color rgba(46,78,73,1)), whites, and calming nature-inspired palettes. The design prioritizes a wellness/meditation aesthetic over scientific precision.

**EEG data display**: Brain activity is abstracted into three states: Calm, Neutral, and Active. Post-session, a line graph shows these states over time. The graph uses color zones to indicate time spent in each state. No raw EEG traces are shown to consumers.

**Feedback visualization**: Real-time audio-based biofeedback -- calm weather sounds for calm brain states, increasing rain/storm sounds for active states. When very calm, birds chirp. Visual feedback is minimal during sessions; the app relies on audio.

**Gamification**: Points and virtual birds earned for calm time. Session summaries show calm percentage, number of birds, and streak tracking. This motivates ongoing practice.

**Sleep tracking**: For Muse S Athena, the app shows EEG-based sleep stages (light, deep, REM), a sleep score, and deep sleep insights.

**Key takeaway**: Muse demonstrates how to present EEG data to non-scientists. The abstraction of raw EEG into meaningful states (calm/neutral/active) with nature metaphors is effective for consumer engagement. Lucid should support both this simplified view and a professional raw-data view.

---

### 1.3 EmotivPRO (Emotiv)

**URL**: https://www.emotiv.com/products/emotivpro

**Layout**: Professional research platform. Multi-panel interface with an integrated EEG viewer showing real-time data streams. Separate panels for Raw EEG, Performance Metrics (focus, stress, engagement), Motion Sensors, and FFT/Band Power.

**Color scheme**: Clean, professional interface described as "intuitive." Dark-themed data visualization panels typical of research software.

**EEG trace display**: Built-in EEG viewer shows scrolling multi-channel traces in real time with event marker support.

**Band powers**: FFT and Band Power data displayed in real time with frequency-domain visualization. Performance metrics (focus, stress, engagement, relaxation) shown as computed scores.

**Topographic maps**: Topographic scalp maps showing frequency band activity across the scalp. Also supports Event-Related Potential (ERP) plots.

**Signal quality**: Contact quality display for all electrodes with color-coded status.

**Session management**: Cloud-based recording storage. Event markers can be added via keyboard, serial port, or USB during recording. Markers appear as vertical lines on the data timeline. Session export to EDF and CSV formats.

**Key takeaway**: EmotivPRO shows how to bridge raw EEG (for researchers) with computed metrics (for practitioners). The dual-view of raw data + performance metrics is valuable.

---

### 1.4 Neurosity (Crown / Console)

**URL**: https://neurosity.co/ | Console at console.neurosity.co

**Layout**: Minimalist, consumer-focused dashboard. The Neurosity Console provides real-time brainwave visualization, focus/calm scores, and kinesis (mental command) training. Mobile apps on iOS and Android.

**Design aesthetic**: Modern, clean Silicon Valley product design. Dark backgrounds with accent colors. Focus on simplicity -- designed by neuroscientists for usability over 3 years.

**Brainwave display**: The console shows raw brainwave visualization alongside computed focus/calm scores. "Shift" visualization shows when the user enters a flow state.

**Focus tracking**: Focus and calm displayed as simple numeric scores with trend visualization. Can connect to Spotify to correlate music with brain states. Can mute notifications based on concentration level.

**Widgets**: Neural Widgets provide at-a-glance brain state summaries.

**Developer tools**: Developer console allows raw EEG visualization, raw data recording, kinesis command training, and focus/calm score access.

**Key takeaway**: Neurosity demonstrates excellent consumer-grade BCI UI/UX. The "Shift" concept (detecting flow states) is a compelling neurofeedback metaphor. Integration with productivity tools (Spotify, notifications) shows how BCI dashboards can extend beyond data display.

---

### 1.5 BrainBay

**URL**: https://github.com/ChrisVeigl/BrainBay

**Layout**: Windows-native Visual Programming Language (VPL) interface. A canvas-based node editor where EEG processing blocks are connected with wires. Separate windows for signal display, FFT, oscilloscope views.

**Design**: Functional but dated Windows UI. Gray backgrounds with colored signal traces. The VPL canvas allows drag-and-drop connection of processing elements.

**Features**: EEG signal display, FFT analysis, biofeedback gaming elements, OSC output. Supports mouse/keyboard control from brain signals. EMG pattern recognition, face tracking via webcam.

**Key takeaway**: BrainBay's node-based processing pipeline is a good concept but the implementation is dated. The idea of visual signal processing chains could inform a future advanced/expert mode in Lucid.

---

### 1.6 NeuroPype (Intheon)

**URL**: https://www.neuropype.io/

**Layout**: Pipeline Designer -- a drag-and-drop visual dataflow programming environment based on the Orange application framework. Single-document application with a canvas for nodes and wires, a toolbar for dragging nodes, and controls for execution and file management.

**Design**: Professional scientific tool aesthetic. Node-based pipeline editor where processing blocks connect to form signal processing chains. Real-time data visualization nodes can be linked into pipelines to monitor state.

**Capabilities**: Hundreds of processing components for noise removal, ERP analysis, spectral analysis, spatial/temporal filtering, 3D brain mapping, connectivity analysis, ML classification, cardiac analysis, and gaze detection.

**Key takeaway**: NeuroPype's pipeline concept is powerful for expert users. The idea of draggable, connectable processing nodes could be adapted as an advanced configuration mode in Lucid. For v1, the dashboard should be simpler.

---

### 1.7 neuromore Studio

**URL**: https://github.com/neuromore/studio

**Layout**: IDE-style interface with multiple dockable panels. Main areas include a node-based visual programming canvas ("Classifier" editor), a live biodata viewer, power spectrograms, and a 3D LORETA brain representation. Completely configurable layout.

**Design**: Professional biofeedback IDE. Dark-themed with multiple simultaneous views. Processing graphs (called "Classifiers") connect input devices to processing nodes and output nodes.

**Visualization**: Raw and processed signals in real-time signal views, power spectrograms, and 3D brain visualization. Feedback visualization for neurofeedback training.

**Key takeaway**: neuromore shows the upper bound of complexity for a BCI dashboard. The dockable panel system with configurable layouts is a good model for power users. Lucid should aim to be between Muse (simple) and neuromore (complex).

---

### 1.8 g.tec g.Recorder

**URL**: https://www.gtec.at/product/g-recorder/

**Layout**: Research-grade biosignal recording software. Main display is a multi-channel trace viewer arranged in a square matrix by default. Supports topographic arrangement loaded from montage files. Channel configuration table shows names and types (EEG, ECG, EMG, EOG, ECoG, etc.).

**EEG display**: Each channel shows a scrolling trace with configurable scaling. The light blue box shows channel name (left) and type (right, e.g., "EEG"). Gray box shows min/max amplitude range. Horizontal dotted gridlines at 0 uV baseline.

**Color customization**: Users can change paper, pen, and grid colors via right-click context menu on channels.

**Montage**: Montage Creator tool defines electrode positions. Channels can be rearranged by rows, columns, or loaded from montage files.

**Evoked potentials**: Separate viewer with averaged data frames per channel, with configurable pre/post-trigger periods.

**Key takeaway**: g.Recorder is the gold standard for clinical EEG display. Its channel info display (name, type, amplitude range, gridlines) should inform Lucid's trace viewer. The montage-based layout system is also worth emulating.

---

### 1.9 Mind Monitor (Third-party Muse app)

**URL**: https://mind-monitor.com/

**Layout**: Mobile app (iOS/Android) providing professional-grade EEG visualization from Muse headbands. Four graph types: Absolute (band powers), Raw (microvolts), Discrete Frequency (log scale), and Spectrogram (heatmap over time).

**Band colors**: Displays Delta, Theta, Alpha, Beta, and Gamma as separate colored traces/bars. Users can split data by channel, left/right brain, front/back, or individual sensors.

**Additional data**: Accelerometer and gyroscope data display.

**Key takeaway**: Mind Monitor is the bridge between Muse's consumer simplicity and professional EEG analysis. Its four graph types (absolute, raw, discrete frequency, spectrogram) map well to Lucid's planned components.

---

### 1.10 Myndlift

**URL**: https://www.myndlift.com/

**Layout**: Two interfaces: (1) Client mobile app with gamified neurofeedback (games, videos, streaming that respond to brain activity), and (2) Clinician dashboard for monitoring clients.

**Clinician dashboard**: Real-time session monitoring, training plan management, before/after brain map comparison, Alpha Peak daily measure, progress quantification, and AI-powered adherence alerts.

**Neurofeedback UI**: Audio, visual, and haptic real-time feedback during sessions. Games and video playback respond to brain state. Training Compass feature for guidance.

**Key takeaway**: Myndlift's split client/clinician model is instructive. The Alpha Peak daily measure and before/after brain map comparisons are excellent features for tracking progress over time.

---

## 2. 2026 React Dashboard Best Practices

### 2.1 CSS Framework: Tailwind CSS v4

**Recommendation: Tailwind CSS v4** -- now the undisputed standard for React dashboards in 2026.

Key v4 changes:
- **CSS-first configuration**: No more `tailwind.config.js`. Everything lives in CSS using `@theme` directive.
- **Dark mode built-in**: Uses `prefers-color-scheme` by default with no configuration. Can be overridden with `@custom-variant` for manual class-based toggling.
- **CSS variables everywhere**: Colors, spacing, and all tokens use CSS custom properties (e.g., `var(--color-primary)`), enabling runtime theming.
- **Performance**: CSS-first approach with zero JavaScript runtime. Better SSR performance than CSS-in-JS alternatives.

Source: https://tailwindcss.com/docs/dark-mode | https://tailwindcss.com/docs/theme

### 2.2 Component Library: shadcn/ui

**Recommendation: shadcn/ui** -- the default choice for React projects in 2026.

Why shadcn/ui for Lucid:
- **75,000+ GitHub stars**, adopted by Vercel, Supabase, and thousands of production apps.
- **Copy-paste components**: Components live in your codebase as local files, not a dependency. Full control over the API and customization.
- **Built on Radix UI primitives**: Accessibility by default (WCAG AA compliant keyboard/screen reader behavior).
- **Tailwind v4 compatible**: Full support for `@theme` directive, `@theme inline`, and CSS-first theming. Updated for React 19.
- **Design quality**: Modern, minimal, polished appearance out of the box.
- **Resizable component**: Built on `react-resizable-panels` (bvaughn), providing panel-based dashboard layouts.

**2026 Best Practice folder structure**:
```
components/
  ui/          # Raw shadcn components (Button, Dialog, etc.)
  primitives/  # Lightly modified (AppButton wrapping Button)
  blocks/      # Product-level compositions (EEGTracePanel, BandPowerCard)
```

**Key principle**: Build product-aware wrappers, not raw component imports. Example: `AppButton` wrapping the base `Button` to inject analytics, loading states, and permission checks globally.

**Alternative considered**: Mantine (120+ components, built-in form management, CSS Modules). Mantine is stronger for enterprise dashboards and has better documentation, but shadcn/ui's ownership model and Tailwind integration make it the better fit for Lucid's custom scientific components.

Sources: https://ui.shadcn.com/docs/tailwind-v4 | https://medium.com/write-a-catalyst/shadcn-ui-best-practices-for-2026-444efd204f44

### 2.3 Dark Mode: Default for Scientific Dashboards

**Recommendation: Dark mode by default**, with light mode as an option.

Rationale:
- Reduces eye strain during extended monitoring sessions.
- Standard across all professional EEG software (OpenBCI, EmotivPRO, neuromore, g.Recorder).
- Better contrast for colored waveforms and heatmaps against dark backgrounds.
- Reduces blue light during neurofeedback training sessions.

**Accessible dark theme guidelines (WCAG 2.2 AA)**:
- **Do not use pure black** (#000000). Use dark grays like `#0a0a0f` or `#121218` to reduce contrast fatigue.
- Regular text: minimum 4.5:1 contrast ratio against background.
- Large text (18pt+ or 14pt bold): minimum 3:1 contrast ratio.
- Non-text elements (icons, borders, chart lines): minimum 3:1 contrast ratio.
- Avoid highly saturated colors on dark backgrounds -- they "vibrate" or bleed. Reduce saturation slightly.
- Use HSL color model for theming: keep hue constant, adjust lightness for different surface levels.

Source: https://blog.greeden.me/en/2026/02/23/complete-accessibility-guide-for-dark-mode-and-high-contrast-color-design-contrast-validation-respecting-os-settings-icons-images-and-focus-visibility-wcag-2-1-aa/

### 2.4 Charting Library for Real-Time Data

**Primary recommendation: Canvas 2D with custom rendering** for EEG traces.

**Secondary recommendation: ChartGPU** (WebGPU-based) for the spectrogram and any views requiring >10,000 data points at 60fps.

**Analysis**:

| Library | Technology | Max Points @60fps | React Integration | License | Best For |
|---------|-----------|-------------------|------------------|---------|----------|
| **ChartGPU** | WebGPU | 35M points @72fps | chartgpu-react | MIT | Spectrograms, scatter density |
| **SciChart.js** | WebGL | Millions | Official React | Commercial ($) | Medical-grade, FDA-cleared apps |
| **Custom Canvas 2D** | Canvas API | ~50K points | Direct | N/A | EEG traces (simple, full control) |
| Recharts | SVG/Canvas | ~10K points | Native React | MIT | Simple charts, band power bars |
| Plotly.js | SVG/WebGL | ~100K points | react-plotly.js | MIT | Interactive exploration |

**Reasoning for Lucid**:

1. **EEG Traces**: 8 channels x 250 SPS x 10s = 20,000 points. Canvas 2D handles this easily and gives full control over rendering (the existing `drawTraces` approach is correct). No library overhead needed.

2. **Spectrogram**: Scrolling 2D heatmap with potentially dense frequency bins. ChartGPU's WebGPU scatter density/heatmap mode is ideal here, or continue with Canvas 2D `putImageData` (current approach) which works fine for modest data sizes.

3. **Band Power bars**: Simple bar chart -- shadcn/ui components with CSS transitions, or Recharts if interactive tooltips are needed.

4. **Topographic map**: Custom Canvas 2D with interpolation (current approach is correct). No charting library needed.

ChartGPU specifics:
- `appendData()` method for real-time updates without full re-renders.
- Multiple charts can share a single GPU device (efficient for dashboards).
- Browser support: Chrome/Edge 113+, Safari 18+, Firefox 145+ (Mac). Full cross-browser WebGPU since January 2026.
- React bindings via `chartgpu-react` package.

Source: https://github.com/ChartGPU/ChartGPU | https://www.scichart.com/demo/react/vital-signs-ecg-medical-chart-example

### 2.5 WebGPU vs Canvas 2D

**WebGPU is now practical in 2026**:
- Full cross-browser support achieved January 2026 (~70% of all browsers).
- Chrome/Edge, Firefox, Safari (including iOS 26) all ship WebGPU.
- 15-30x performance improvement over WebGL for compute workloads.
- Libraries like ChartGPU demonstrate 1M+ points at 60fps.

**Recommendation for Lucid**:
- **Canvas 2D for EEG traces**: The data volume (20K points) is well within Canvas 2D's capability. Custom rendering gives full control, avoids dependencies, and is simpler to maintain.
- **WebGPU (via ChartGPU or WASM DSP output) for spectrogram**: When implementing high-resolution spectrograms with many frequency bins, WebGPU becomes advantageous.
- **Canvas 2D for topographic map**: Inverse distance weighting interpolation at 4px steps is fast enough on Canvas 2D.
- **Reserve WebGPU for future**: Multi-channel raw data replay, high-density electrode arrays (32+ channels), and ML feature visualization.

Source: https://byteiota.com/webgpu-2026-70-browser-support-15x-performance-gains/

### 2.6 Layout: Resizable Multi-Panel Dashboard

**Recommendation: react-resizable-panels + CSS Grid**

Two layout libraries dominate in 2026:

| Feature | react-resizable-panels | react-grid-layout |
|---------|----------------------|-------------------|
| Primary use | Split-pane resizing | Drag-and-drop grid |
| Interaction | Resize handles | Drag + resize |
| Integration | shadcn/ui Resizable component | Standalone |
| Complexity | Low | Medium |
| Serialization | Built-in | Built-in |
| Accessibility | Keyboard resizing, ARIA | Basic |
| Best for | IDE-like layouts | Widget dashboards |

**Recommendation**: Start with **react-resizable-panels** (already integrated into shadcn/ui as the `Resizable` component). This provides:
- Horizontal and vertical split panes.
- Collapsible panels (e.g., collapse sidebar).
- Persistent layout via localStorage.
- Keyboard-accessible resize handles.
- Nested panel groups for complex layouts.

Later, optionally add **react-grid-layout** for a user-customizable widget arrangement mode (like OpenBCI GUI's 12 layouts).

**Proposed layout structure**:
```
+--------------------------------------------------+
|  Header: Lucid | Device Status | Session Controls |
+------+-------------------------------------------+
|      |  Main Visualization Area                   |
| Side |  +--------------------+------------------+ |
| bar  |  | EEG Traces         | Spectrogram      | |
|      |  | (resizable)        | (resizable)      | |
| Nav  |  +--------------------+------------------+ |
|      |  | Band Power | Topo  | Neurofeedback    | |
|      |  |            | Map   |                  | |
|      |  +------------+-------+------------------+ |
+------+-------------------------------------------+
|  Footer: Recording status | Epoch count | Latency |
+--------------------------------------------------+
```

Sources: https://github.com/bvaughn/react-resizable-panels | https://ui.shadcn.com/docs/components/radix/resizable

### 2.7 Typography

**Recommendation**:
- **Labels and UI text**: Inter -- the standard UI typeface in 2026. Tall x-height for readability at small sizes, tabular numbers for aligned data, contextual alternates.
- **Numeric data and channel labels**: JetBrains Mono -- designed for code/data display. Standard width characters keep columns aligned. Tall x-height matches Inter closely for visual harmony.
- **System font stack fallback**: `-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif` for zero-load-time rendering.

**Typography scale for data-dense dashboards**:
- Panel headers: 14px Inter semibold
- Channel labels: 11px JetBrains Mono
- Numeric values: 12px JetBrains Mono (tabular figures)
- Axis labels: 10px JetBrains Mono
- Section titles: 16px Inter medium
- Top-level navigation: 14px Inter medium

Both fonts are free, open source, and available on Google Fonts.

Source: https://www.jetbrains.com/lp/mono/ | https://fonts.google.com/specimen/JetBrains+Mono

### 2.8 Animation and Live Data Updates

**Recommendations**:

1. **Use `requestAnimationFrame`** for all canvas-based rendering (EEG traces, spectrogram, topo map). Batch DOM reads/writes to avoid layout thrashing. The current Lucid approach is correct.

2. **Use `useRef` for frame-by-frame mutable state**, not `useState`. React state updates trigger re-renders; refs allow imperatively updating DOM elements during animation frames without re-render overhead.

3. **CSS transitions for non-canvas UI**: Band power bars, status indicators, panel resizing. Animate `transform` and `opacity` only -- these are GPU-composited and do not trigger layout.

4. **Minimal animation on data-heavy dashboards**: AutoAnimate or React Transition Group are safer choices than complex layout animations. Avoid animating large containers that rerender frequently due to filtering, pagination, or live data.

5. **Motion library** (formerly Framer Motion) is the best overall React animation library in 2026 for mount/unmount transitions, shared layout animations, and gesture-driven interactions. Use sparingly for panel transitions, not for per-frame data.

6. **View Transitions API** for larger navigation changes (switching between dashboard views).

Source: https://www.benedikt-sperl.de/blog/2026-01-13-animations-on-the-web

---

## 3. EEG-Specific UI Patterns

### 3.1 Multi-Channel EEG Trace Display

**Clinical standard**: Vertically stacked traces, each channel in its own horizontal band with a baseline at center. This is universally used in clinical EEG (ILAE/IFCN/ACNS standards).

**Display parameters** (per ACNS/ILAE guidelines):
- Display window: 10-20 seconds per page (corresponding to ~30mm/sec paper speed).
- Allow simultaneous display of multiple segments for visual comparison.
- Standardized montages for consistency across sessions.

**Implementation patterns**:
- **Scrolling** (continuous): Data scrolls right-to-left in real time. Most common for live monitoring. Used by OpenBCI GUI, g.Recorder, EmotivPRO.
- **Sweeping/FIFO** (wrap-around): New data sweeps across the screen and wraps back to the start. A vertical "sweep line" marks the current position. Common in medical monitors (ECG style). Used by SciChart medical demo.
- **Paged** (epoch-based): Show a fixed window of data, advance to next page manually or on timer. Used for offline review and clinical scoring.

**Recommendation for Lucid**: Default to **scrolling** mode for live monitoring, with **sweeping** as an option for neurofeedback training (more stable visually), and **paged** for session review/playback.

### 3.2 EEG Frequency Band Colors

There is no universal standard for band colors, but several conventions have emerged across tools. Here is a recommended palette for Lucid, designed for dark backgrounds with good perceptual separation and accessibility:

| Band | Frequency | Recommended Color | Hex | Rationale |
|------|-----------|------------------|-----|-----------|
| Delta | 0.5-4 Hz | Indigo | `#818cf8` | Slowest rhythm; cool color anchors the low end |
| Theta | 4-8 Hz | Violet | `#a78bfa` | Adjacent to delta; purple bridges cool and warm |
| Alpha | 8-13 Hz | Cyan | `#22d3ee` | Distinctive; alpha is the most clinically prominent band |
| Beta | 13-30 Hz | Emerald | `#34d399` | Warm-shift begins; active/engaged state |
| Gamma | 30-100 Hz | Amber | `#fbbf24` | Warmest; highest frequency gets warmest color |

This follows a **cool-to-warm spectral progression** matching low-to-high frequency, which is intuitively mappable and has good perceptual ordering. All colors meet WCAG AA contrast against `#0a0a1a` background.

The current Lucid codebase uses:
- Delta: `#6366f1` (indigo-500), Theta: `#8b5cf6` (violet-500), Alpha: `#06b6d4` (cyan-500), Beta: `#22c55e` (green-500), Gamma: `#f59e0b` (amber-500).

**Assessment**: The existing Lucid colors are very good. Slight adjustments recommended above for better contrast on dark backgrounds (lighter variants from Tailwind 400-level instead of 500).

### 3.3 Spectrogram Colormaps

**Critical guidance from "Over the Rainbow" (NeuroImage, 2021)**:

The rainbow colormap (jet) is demonstrably harmful for scientific visualization:
- Produces perceptual artifacts (false contours at yellow-green and cyan boundaries).
- Creates "flat" bands where perceptually uniform data appears stepped.
- Inaccessible to color-vision-deficient viewers (~5% of population).

**Recommended colormaps**:

| Colormap | Type | Best For | CVD Safe |
|----------|------|----------|----------|
| **Viridis** | Sequential | General purpose spectrograms | Yes |
| **Cividis** | Sequential | Maximum CVD accessibility | Yes (designed for it) |
| **Inferno** | Sequential | High dynamic range data | Yes |
| **Plasma** | Sequential | Publication figures | Yes |
| **RdBu** (diverging) | Diverging | Topographic maps (above/below baseline) | Moderate |

**Recommendation for Lucid**:
- **Spectrogram**: Use **viridis** as default. Offer cividis as a CVD-accessible alternative.
- **Topographic map**: Use **RdBu** (diverging, red-blue) for power maps showing deviations from baseline. Use viridis for absolute power.
- **Replace the current rainbow colormap** in both Spectrogram.tsx and TopoMap.tsx. The current `blue->cyan->green->yellow->red` mapping is essentially the jet/rainbow colormap and should be replaced with viridis.

Implementation: Pre-compute a 256-entry lookup table from the viridis color scale. Map normalized values [0,1] to the table. This is trivially fast and avoids per-pixel computation.

Source: https://www.sciencedirect.com/science/article/pii/S1053811921009010

### 3.4 Topographic Map Rendering

**MNE-Python reference implementation** (the gold standard):
- Uses CloughTocher2DInterpolator (cubic) for smooth interpolation between electrodes.
- Extrapolation modes: 'local' (near sensors only), 'head' (to head circle), or 'box'.
- Default colormap: 'Reds' for all-positive data, 'RdBu_r' (diverging) for mixed.
- Standard 10-20 montage built in.

**For Lucid's JavaScript/Canvas implementation**:
- The current inverse distance weighting (IDW) approach in TopoMap.tsx is functional but can produce "bullseye" artifacts around electrodes.
- **Upgrade path**: Use a JavaScript port of scipy's CloughTocher2D or implement Delaunay triangulation with barycentric interpolation for smoother results.
- **Libraries**: `d3-delaunay` for triangulation, then barycentric interpolation within triangles.
- **Head outline**: Draw head circle, nose triangle (current approach), and ear indicators. Show electrode positions as small dots with labels.
- **Resolution**: 4px step (current) is acceptable for 200px canvas. For larger displays, consider 2px step or use `OffscreenCanvas` + `drawImage` for scaling.

### 3.5 Spectrogram Display Patterns

**Three patterns**:

1. **Scrolling heatmap** (recommended for live monitoring): New data rows appear at one edge, oldest data drops off the other edge. Frequency on Y-axis, time on X-axis, color = power. This is the standard clinical spectrogram.

2. **Waterfall**: 3D-perspective stacked lines showing frequency spectra over time. More visually dramatic but harder to read quantitatively.

3. **Static heatmap**: Full spectrogram for a completed recording. Time on X-axis, frequency on Y-axis. Best for post-session review.

**Implementation best practice (per Canvas/JS spectrogram research)**:
- Build spectrogram off-screen by writing pixel colors into an off-screen canvas ImageData buffer.
- Each row of data maps to a row of pixels. Successive rows are adjacent.
- Use `ctx.drawImage(offscreenCanvas, ...)` for efficient on-the-fly scaling.
- When input reaches the last pixel row, wrap to the first row with a marker line.
- Use typed arrays (`Float32Array`) for data buffers to avoid GC pressure.

**Recommendation for Lucid**: The current `putImageData` approach in Spectrogram.tsx is correct in principle. Optimize by pre-computing the viridis LUT and using `OffscreenCanvas` for the scrolling buffer.

### 3.6 Signal Quality Indicators

**Industry patterns**:

| System | Method | Display |
|--------|--------|---------|
| OpenBCI | Impedance check | Green/yellow/red circles per channel |
| BrainAccess | Real-time quality | Red/yellow/green tri-state per electrode |
| EmotivPRO | Contact quality | Color-coded electrode map |
| g.tec | Impedance measurement | Numeric ohm values + color coding |
| Muse | Signal quality | Good/poor text per sensor |

**Recommendation for Lucid**:
- **Topographic electrode map** with color-coded dots (green/yellow/red) as primary indicator.
- **Numeric impedance values** shown on hover/click.
- **Channel header** in EEG trace view shows a small colored dot next to each channel label.
- **Tri-state classification**: Good (green, <10k ohm) / Marginal (yellow, 10-50k ohm) / Poor (red, >50k ohm or disconnected). Note: these thresholds are for dry electrodes and should be configurable.

### 3.7 Neurofeedback Training UI Patterns

**Research-backed patterns**:

1. **Audio feedback** (most common): Continuous tone, nature sounds, or music that changes based on brain state. Muse uses weather sounds. Myndlift uses game audio.

2. **Visual feedback**:
   - **Screen dimming**: Display dims when brain drifts from target state, brightens when on-target. Used by many clinical systems.
   - **Video playback control**: Video plays normally when on-target, pauses/shrinks when off-target. Used by Myndlift.
   - **Simple gauge/meter**: A bar, circle, or arc that fills based on the target metric. Best for precise training.
   - **Animated scene**: A landscape, particle system, or abstract visualization that responds to brain state. Most engaging.
   - **VR environments**: Emerging pattern -- immersive environments for neurofeedback.

3. **Reward/inhibit indicators**: Clear visual separation between reward bands (encouraged) and inhibit bands (discouraged). Green = reward active, red/amber = inhibit triggered.

4. **Progress tracking**: Session-over-session trend charts. Before/after brain maps. Alpha Peak daily measure (Myndlift).

**Recommendation for Lucid**:
- **Primary feedback**: A central animated element (pulsing orb, breathing circle, or abstract particle system) that responds to the reward band in real time.
- **Secondary feedback**: Audio tone or nature sounds (optional, user-controlled).
- **Training metrics**: Target band power shown as a real-time gauge with threshold markers. Reward percentage counter. Session timer.
- **Post-session summary**: Time-series of the training metric, percentage above threshold, comparison to previous sessions.

### 3.8 Session Management UI

**Patterns from EmotivPRO and clinical systems**:

- **Timeline with event markers**: Horizontal timeline at the bottom of the screen showing recording duration. Vertical marker lines for events. Click markers to jump to that point.
- **Recording controls**: Record/stop/pause buttons. Red dot indicator when recording.
- **Session list**: Sorted by date, showing name, duration, protocol used, and status (complete/interrupted).
- **Playback controls**: Play/pause, speed control (0.5x-4x), seek bar, epoch navigation.
- **Export options**: EDF+, CSV, JSON.
- **Annotations**: Text notes attached to time points.

---

## 4. Specific Design Recommendations for Lucid

### 4.1 Recommended Color Palette (Dark Theme)

```css
/* Background surfaces (darkest to lightest) */
--bg-base:       #09090b;  /* zinc-950 - main background */
--bg-surface:    #18181b;  /* zinc-900 - card/panel backgrounds */
--bg-elevated:   #27272a;  /* zinc-800 - elevated surfaces, hover states */
--bg-overlay:     #3f3f46;  /* zinc-700 - overlays, dropdowns */

/* Text */
--text-primary:   #fafafa;  /* zinc-50 - primary text */
--text-secondary: #a1a1aa;  /* zinc-400 - secondary text, labels */
--text-tertiary:  #71717a;  /* zinc-500 - disabled, placeholder */

/* Borders */
--border-default: #27272a;  /* zinc-800 */
--border-hover:   #3f3f46;  /* zinc-700 */

/* EEG Band Accent Colors (cool-to-warm progression) */
--band-delta:     #818cf8;  /* indigo-400 */
--band-theta:     #a78bfa;  /* violet-400 */
--band-alpha:     #22d3ee;  /* cyan-400 */
--band-beta:      #34d399;  /* emerald-400 */
--band-gamma:     #fbbf24;  /* amber-400 */

/* Channel trace colors (8-color cycle, distinct hues) */
--ch-1:           #818cf8;  /* indigo-400 */
--ch-2:           #c084fc;  /* purple-400 */
--ch-3:           #22d3ee;  /* cyan-400 */
--ch-4:           #34d399;  /* emerald-400 */
--ch-5:           #fbbf24;  /* amber-400 */
--ch-6:           #fb923c;  /* orange-400 */
--ch-7:           #f87171;  /* red-400 */
--ch-8:           #2dd4bf;  /* teal-400 */

/* Semantic colors */
--success:        #22c55e;  /* green-500 */
--warning:        #f59e0b;  /* amber-500 */
--error:          #ef4444;  /* red-500 */
--info:           #3b82f6;  /* blue-500 */

/* Signal quality */
--signal-good:    #22c55e;  /* green */
--signal-marginal:#f59e0b;  /* amber */
--signal-poor:    #ef4444;  /* red */

/* Neurofeedback */
--reward-active:  #22c55e;  /* green - reward state */
--reward-inactive:#27272a;  /* zinc-800 */
--inhibit-active: #f59e0b;  /* amber - inhibit triggered */

/* Spectrogram/Topo colormaps: implement as LUTs, not CSS */
/* Use viridis for sequential data, RdBu for diverging */
```

### 4.2 Recommended Layout

**Pattern**: Sidebar navigation + resizable multi-panel main area.

```
+------------------------------------------------------------------+
| Header Bar                                                         |
| [Lucid logo] [Device: Muse 2 (connected)] [Rec: 00:05:32] [gear] |
+----------+-------------------------------------------------------+
|          |  +-------------------------+-------------------------+ |
| Sidebar  |  |                         |                         | |
|          |  |    EEG Traces           |    Spectrogram          | |
| [waves]  |  |    (scrolling)          |    (heatmap)            | |
| [spec]   |  |                         |                         | |
| [topo]   |  +-------------------------+-------------------------+ |
| [bands]  |  |            |            |                         | |
| [neuro]  |  | Band Power | Topo Map   |    Neurofeedback       | |
| [session]|  | (bars)     | (interp)   |    (training UI)       | |
| [settings]| |            |            |                         | |
|          |  +------------+------------+-------------------------+ |
+----------+-------------------------------------------------------+
| Footer: Epoch #1234 | Latency: 12ms | Buffer: 98% | 250 SPS     |
+------------------------------------------------------------------+
```

**Sidebar**: Collapsible, icon + text labels. Each icon navigates to a different view or toggles panel visibility. At narrow widths, sidebar collapses to icons only.

**Main area**: Resizable panels using shadcn/ui `Resizable` (react-resizable-panels). EEG traces get the most vertical space (primary visualization). Panels can be collapsed or expanded.

**Header**: Fixed top bar with device connection status, recording indicator, and settings access.

**Footer**: Status bar showing real-time metrics: epoch count, network latency, buffer status, sample rate.

### 4.3 Recommended Component Library

**Primary: shadcn/ui** with Tailwind CSS v4 and Radix UI primitives.

Justification:
1. Already the industry standard for React 19 projects in 2026.
2. Full code ownership -- critical for scientific software that needs pixel-perfect control.
3. Radix UI provides accessible primitives (dialogs, dropdowns, tooltips, sliders) without opinionated styling.
4. The `Resizable` component (wrapping react-resizable-panels) provides the dashboard panel layout.
5. Tailwind v4's CSS variable system enables runtime theme switching (dark/light, custom accent colors).
6. Zero runtime cost -- no CSS-in-JS overhead.
7. Lucid's web stack already uses React 19, TypeScript 5.7, Vite 6, and Tailwind v4 (per CLAUDE.md).

**Supplementary**:
- `react-resizable-panels` via shadcn/ui Resizable (panel layout).
- `ChartGPU` / `chartgpu-react` (WebGPU charts for spectrogram when needed).
- Custom Canvas 2D rendering for EEG traces, topo map, spectrogram (current approach, refined).
- `Motion` (formerly Framer Motion) for mount/unmount transitions only (e.g., panel open/close).

### 4.4 Recommended Typography

```css
/* Font imports */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* Or use @fontsource for self-hosted (better performance) */
/* @fontsource/inter, @fontsource/jetbrains-mono */

:root {
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', 'Cascadia Code', 'Fira Code', monospace;
}

/* Usage patterns */
body          { font-family: var(--font-sans); font-size: 14px; }
.panel-title  { font-family: var(--font-sans); font-weight: 600; font-size: 14px; }
.section-title{ font-family: var(--font-sans); font-weight: 500; font-size: 16px; }
.channel-label{ font-family: var(--font-mono); font-size: 11px; }
.data-value   { font-family: var(--font-mono); font-size: 12px; font-variant-numeric: tabular-nums; }
.axis-label   { font-family: var(--font-mono); font-size: 10px; }
.status-text  { font-family: var(--font-mono); font-size: 11px; }
```

### 4.5 Responsive Layout Strategy

**Approach**: CSS Grid + react-resizable-panels + Tailwind responsive breakpoints.

- **Desktop (1280px+)**: Full multi-panel layout as shown above. All panels visible.
- **Laptop (1024-1279px)**: Sidebar collapses to icons. Panels stack 2 columns instead of 3.
- **Tablet (768-1023px)**: Sidebar becomes bottom tab bar. Panels stack vertically. Only one primary visualization shown at a time (tabs to switch).
- **Mobile (< 768px)**: Single column. Tab navigation. Optimized for neurofeedback training (simple feedback view) rather than full data analysis.

Use Tailwind's responsive prefixes: `md:`, `lg:`, `xl:` for breakpoint-specific styles. `react-resizable-panels` handles persistence of user-customized panel sizes.

### 4.6 Component-Specific Recommendations

#### EEG Trace Viewer
- **Keep Canvas 2D** rendering (current approach is correct for 8ch x 250SPS).
- **Replace hardcoded colors** with CSS variable-driven channel colors.
- **Add channel controls**: Per-channel amplitude scaling (dropdown or scroll), channel on/off toggle.
- **Add time axis**: Bottom axis with second markers.
- **Add amplitude scale bar**: Vertical bar showing uV scale.
- **Support display modes**: Scrolling (default), sweeping (for neurofeedback), paged (for review).
- **Add grid overlay**: Subtle dotted grid lines for time/amplitude reference.
- **Channel labels**: Use JetBrains Mono 11px, color-matched to trace.

#### Spectrogram
- **Replace rainbow colormap** with viridis (pre-computed 256-entry LUT).
- **Add frequency axis**: Left axis showing Hz labels.
- **Add time axis**: Bottom axis showing seconds.
- **Add color scale bar**: Right side showing the viridis gradient with dB/power labels.
- **Use OffscreenCanvas**: Render to off-screen buffer, then `drawImage` to visible canvas for smooth scrolling.
- **Add channel selector**: Dropdown to select which channel's spectrogram to display.
- **Configuration**: Max frequency (default 50Hz), time window, log/linear power scale.

#### Topographic Map
- **Replace rainbow colormap** with RdBu (diverging) for relative power or viridis for absolute.
- **Improve interpolation**: Consider Delaunay triangulation + barycentric interpolation for smoother results (vs current IDW).
- **Add color scale bar**: Side bar showing the color gradient with power values.
- **Add band selector**: Toggle between delta/theta/alpha/beta/gamma topographic views.
- **Add electrode quality overlay**: Show signal quality dots on electrode positions.
- **Increase resolution**: Use 2px step for cleaner appearance on modern displays.
- **Add ear indicators**: Small bumps on left/right of head outline.

#### Band Power Display
- **Use horizontal bars** (not vertical) to better fit dashboard panels.
- **Add animation**: Smooth CSS transitions on bar width changes (300ms ease-out).
- **Show raw values**: Numeric power value at end of each bar in JetBrains Mono.
- **Add relative mode**: Show percentage of total power per band.
- **Add per-channel view**: Toggle between averaged (all channels) and per-channel band powers.
- **Color each bar** with its band color from the standardized palette.

#### Neurofeedback Panel
- **Central feedback element**: A pulsing circle or orb that grows/glows green when reward is active, dims when off-target.
- **Training metric gauge**: Arc/ring gauge showing the target band power value relative to threshold.
- **Threshold line**: Clear visual marker on the gauge showing the reward threshold.
- **Session timer**: Prominent countdown or elapsed timer.
- **Reward counter**: Running tally of time above threshold (percentage and seconds).
- **Protocol info**: Protocol name, target band, reward band, inhibit band, with color coding.
- **History chart**: Small sparkline showing the last 60 seconds of the training metric.
- **Post-session view**: Summary statistics, comparison to previous sessions.

#### Session Manager
- **Timeline control**: Horizontal timeline with scrubber, play/pause, speed controls (0.5x-4x).
- **Event markers**: Vertical lines on timeline, clickable to jump to that moment.
- **Session list**: Card layout with session name, date, duration, protocol, and status badge.
- **Recording indicator**: Red pulsing dot when actively recording.
- **Export buttons**: EDF+, CSV, JSON export with progress indicator.
- **Session notes**: Text area for annotations.

#### Device Connection
- **Connection card**: Shows device type, name, battery level, signal quality summary.
- **Electrode map**: Small head diagram with electrode dots colored by signal quality.
- **Connection wizard**: Step-by-step guided connection for first-time users.
- **Status dot**: Green=connected, yellow=connecting, red=error, gray=disconnected.
- **Device selector dropdown**: For choosing between multiple available devices.
- **Board configuration**: Select BrainFlow board ID or LSL stream.

---

## 5. Key Sources

### Commercial EEG Software
- [OpenBCI GUI Documentation](https://docs.openbci.com/Software/OpenBCISoftware/GUIDocs/)
- [OpenBCI GUI Widget Guide](https://docs.openbci.com/Software/OpenBCISoftware/GUIWidgets/)
- [OpenBCI GUI v5 Release](https://openbci.com/community/gui-v5-release/)
- [EmotivPRO EEG Analysis Platform](https://www.emotiv.com/blogs/news/emotivpro-eeg-analysis-platform)
- [EmotivPRO Product Page](https://www.emotiv.com/products/emotivpro)
- [Muse App](https://choosemuse.com/pages/app)
- [Muse App Updates](https://choosemuse.com/blogs/news/whats-new-in-the-muse-app-smarter-dashboard-for-brain-health-and-mental-fitness)
- [Neurosity Crown](https://neurosity.co/crown)
- [Neurosity Console Demo](https://neurosity.co/blog/experience-neurositys-free-demo)
- [g.tec g.Recorder](https://www.gtec.at/product/g-recorder/)
- [NeuroPype](https://www.neuropype.io/)
- [neuromore Studio](https://github.com/neuromore/studio)
- [BrainBay](https://github.com/ChrisVeigl/BrainBay)
- [Mind Monitor](https://mind-monitor.com/)
- [Myndlift](https://www.myndlift.com/for-mental-health-practitioners)

### 2026 React Stack
- [shadcn/ui Best Practices 2026](https://medium.com/write-a-catalyst/shadcn-ui-best-practices-for-2026-444efd204f44)
- [shadcn/ui Tailwind v4 Support](https://ui.shadcn.com/docs/tailwind-v4)
- [Best React UI Component Libraries 2026](https://www.untitledui.com/blog/react-component-libraries)
- [Mantine vs shadcn/ui Comparison](https://saasindie.com/blog/mantine-vs-shadcn-ui-comparison)
- [Tailwind CSS v4 Dark Mode](https://tailwindcss.com/docs/dark-mode)
- [Tailwind CSS v4 Theme Variables](https://tailwindcss.com/docs/theme)

### Charting & Visualization
- [ChartGPU (WebGPU charting)](https://github.com/ChartGPU/ChartGPU)
- [ChartGPU React Bindings](https://github.com/ChartGPU/chartgpu-react)
- [SciChart React Medical Demo](https://www.scichart.com/demo/react/vital-signs-ecg-medical-chart-example)
- [WebGPU 2026 Browser Support](https://byteiota.com/webgpu-2026-70-browser-support-15x-performance-gains/)

### Layout
- [react-resizable-panels](https://github.com/bvaughn/react-resizable-panels)
- [shadcn/ui Resizable](https://ui.shadcn.com/docs/components/radix/resizable)
- [react-grid-layout](https://github.com/react-grid-layout/react-grid-layout)

### Scientific Visualization Standards
- [Over the Rainbow: Color Maps in Neurophysiology (NeuroImage, 2021)](https://www.sciencedirect.com/science/article/pii/S1053811921009010)
- [Viridis Color Maps](https://cran.r-project.org/web/packages/viridis/vignettes/intro-to-viridis.html)
- [Color Map Advice for Scientific Visualization](https://www.kennethmoreland.com/color-advice/)
- [WCAG Dark Mode Accessibility Guide](https://blog.greeden.me/en/2026/02/23/complete-accessibility-guide-for-dark-mode-and-high-contrast-color-design-contrast-validation-respecting-os-settings-icons-images-and-focus-visibility-wcag-2-1-aa/)
- [MNE-Python Topographic Maps](https://mne.tools/stable/generated/mne.viz.plot_topomap.html)

### Typography
- [JetBrains Mono](https://www.jetbrains.com/lp/mono/)
- [Inter Typeface](https://rsms.me/inter/)

### Clinical EEG Standards
- [ACNS Guidelines](https://www.acns.org/practice/guidelines)
- [ILAE/IFCN Minimum EEG Standards](https://www.ilae.org/files/dmfile/eeg-minimum-standards.pdf)
- [BrainAccess EEG Signal Quality](https://www.brainaccess.ai/tutorials/eeg-signal-quality/)

### Animation & Performance
- [Animations on the Web (2026)](https://www.benedikt-sperl.de/blog/2026-01-13-animations-on-the-web)
- [React Animation Libraries Comparison](https://www.syncfusion.com/blogs/post/react-animation-libraries-comparison)
- [EEG Session Markers (EmotivPRO)](https://emotiv.gitbook.io/emotivpro-v3/event-markers/about)
