# Accessibility Checklist (WCAG 2.1 AA)

> Ensure your application is usable by everyone.

## Keyboard Navigation

- [ ] All interactive elements focusable with Tab
- [ ] Focus order is logical (follows visual order)
- [ ] Focus indicator visible (never `outline: none`)
- [ ] Skip link to main content
- [ ] No keyboard traps
- [ ] Custom components work with Enter/Space

```html
<!-- ✅ Better: Use native button -->
<button @click="handleClick">Click me</button>

<!-- ✅ If custom element needed: use role + keyboard handler -->
<div
  role="button"
  tabindex="0"
  @click="handleClick"
  @keydown.enter="handleClick"
  @keydown.space.prevent="handleClick"
>
  Click me
</div>
```

## Screen Readers

### Semantic HTML

- [ ] Use semantic elements (`<nav>`, `<main>`, `<article>`, etc.)
- [ ] Headings in logical order (h1 → h2 → h3)
- [ ] Lists use `<ul>`, `<ol>`, `<dl>`
- [ ] Tables have `<th>` with scope

### ARIA

- [ ] Images have alt text (empty `alt=""` for decorative)
- [ ] Form inputs have labels
- [ ] Buttons have accessible names
- [ ] Dynamic content announced (aria-live)
- [ ] Modals trap focus and have aria-modal

```html
<!-- ✅ Accessible form (Vue) -->
<label for="email">Email</label>
<input id="email" type="email" aria-describedby="email-hint" />
<span id="email-hint">We'll never share your email</span>

<!-- ✅ Accessible icon button -->
<button aria-label="Close menu">
  <CloseIcon aria-hidden="true" />
</button>

<!-- ✅ Live region for updates -->
<div aria-live="polite" aria-atomic="true">{{ notification }}</div>
```

## Visual Design

### Color

- [ ] Color contrast ratio ≥ 4.5:1 (text)
- [ ] Color contrast ratio ≥ 3:1 (large text, UI components)
- [ ] Information not conveyed by color alone
- [ ] Links distinguishable from text (underline or contrast)

### Text

- [ ] Text resizable to 200% without loss
- [ ] Line height ≥ 1.5
- [ ] No text in images (except logos)

### Motion

- [ ] Respect `prefers-reduced-motion`
- [ ] No flashing content (> 3 flashes/second)
- [ ] Animations can be paused

```css
/* Respect motion preferences */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Forms

- [ ] All inputs have visible labels
- [ ] Required fields marked
- [ ] Error messages associated with inputs
- [ ] Autocomplete attributes used
- [ ] Form validation accessible

```html
<!-- ✅ Accessible error message (Vue) -->
<input
  id="email"
  :aria-invalid="hasError"
  :aria-describedby="hasError ? 'email-error' : undefined"
/>
<span v-if="hasError" id="email-error" role="alert">
  Please enter a valid email address
</span>
```

## Interactive Components

### Buttons & Links

- [ ] Buttons for actions, links for navigation
- [ ] Link text is descriptive (not "click here")
- [ ] Disabled state communicated

### Modals/Dialogs

- [ ] Focus trapped inside modal
- [ ] Close with Escape key
- [ ] Focus returns on close
- [ ] `role="dialog"` and `aria-modal="true"`

### Menus & Dropdowns

- [ ] Arrow key navigation
- [ ] `role="menu"` and `role="menuitem"`
- [ ] Current item indicated

## Testing Tools

```bash
# Automated testing
npx axe-cli https://example.com
npx pa11y https://example.com

# Browser extensions
- axe DevTools (Chrome)
- WAVE (Chrome/Firefox)
- Accessibility Insights (Chrome)
```

### Manual Testing

- [ ] Navigate with keyboard only
- [ ] Test with screen reader (VoiceOver/NVDA)
- [ ] Zoom to 200%
- [ ] Use high contrast mode
- [ ] Test with reduced motion

## ARIA Roles Quick Reference

| Role                         | Use For                                |
| ---------------------------- | -------------------------------------- |
| `button`                     | Clickable elements (prefer `<button>`) |
| `link`                       | Navigation (prefer `<a>`)              |
| `dialog`                     | Modal windows                          |
| `alert`                      | Important messages                     |
| `status`                     | Status updates                         |
| `navigation`                 | Nav sections (prefer `<nav>`)          |
| `main`                       | Main content (prefer `<main>`)         |
| `region`                     | Distinct sections with label           |
| `tablist`, `tab`, `tabpanel` | Tab interfaces                         |

## Common Issues

| Issue                   | Fix                               |
| ----------------------- | --------------------------------- |
| Missing alt text        | Add descriptive alt or `alt=""`   |
| Low contrast            | Increase color contrast           |
| Missing form labels     | Add `<label>` elements            |
| Focus not visible       | Don't remove outline, style it    |
| Mouse-only interactions | Add keyboard handlers             |
| Auto-playing media      | Add controls, respect preferences |
