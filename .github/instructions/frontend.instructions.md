---
description:
  'frontend patterns (Django templates + HTMX + django-cotton + Alpine +
  Tailwind/daisyUI)'
applyTo: 'src/**/templates/**/*.html,src/**/static/**/*,src/templates/**/*.html,src/static/**/*'
---

# Frontend Development Guide

Frontend development for this project is **server-rendered first** (Django
templates) with **HTMX** for partial updates, **django-cotton** for reusable
template components, **Alpine** for lightweight interactivity, and **Tailwind +
daisyUI** for a consistent premium UI.

## Technology Stack Overview

- **Django templates**: server-side rendering with `extends` + `{% block %}`
- **django-cotton**: reusable UI components in `templates/cotton/` with `<c-*>`
  syntax
- **HTMX (+ django-htmx)**: progressive enhancement via HTML attributes +
  HTMX-aware server responses
- **Alpine.js**: small interactive behaviors (modals, toasts, pickers,
  micro-interactions)
- **Tailwind CSS + daisyUI**: utility-first + component classes; use custom
  themes `project` / `project-dark`

## General Frontend Principles

- **Progressive enhancement**: pages must work as normal HTML; HTMX/Alpine only
  enhance.
- **Mobile-first**: default layouts and touch targets for phones; enhance for
  desktop/TV.
- **Consistency**: use the shared component library (Cotton/components/partials)
  instead of one-off markup.
- **Accessibility**: minimum WCAG AA contrast, keyboard support, and clear focus
  states.

## Project Structure (Frontend Files)

- Templates live under `src/templates/` (project-wide) and
  `src/<app>/templates/<app>/` (app-owned, namespaced to avoid collisions).
- Static assets live under `src/static/` (project-wide) and
  `src/<app>/static/<app>/` (app-owned, namespaced).
- Cotton components should live under `src/templates/cotton/` (or app-level
  `templates/cotton/`) so they can be used everywhere.
- Base template: `src/templates/_base.html` loads static assets, HTMX, Alpine,
  and defines standard blocks.
- Use `{% load static %}` in templates that reference static files.

### Template loading pattern

```django
{% load static %}
<!DOCTYPE html>
<html lang="en" data-theme="app">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'css/styles.css' %}">
    {% block head %}{% endblock %}
</head>
<body>
    {% block content %}{% endblock %}
    {% block scripts %}{% endblock %}
</body>
</html>
```

## Theme & UI System (Premium Layout)

- Use daisyUI component classes (`btn`, `card`, `badge`, `navbar`, etc.) with
  Tailwind utilities for layout.
- Implement and use a custom daisyUI theme:
  - Light: `<project-name>` (e.g., `app`)
  - Dark: `<project-name>-dark` (e.g., `app-dark`)
- Prefer setting the theme via `data-theme` (e.g., `<html data-theme="app">`),
  and keep dark mode as a theme switch (not a separate CSS system).
- Typography: prefer **Inter** (or system fallback).
- Interaction constraints: animations should be subtle and fast; avoid complex
  motion.

## django-cotton Component Guidelines

Prefer Cotton for shared UI building blocks (buttons, inputs, chips, cards,
modal shells).

**Core principles:**

- Keep components **purely presentational** (no DB queries; minimal branching)
- Expose customization via attributes, and allow pass-through HTML attributes
  via `{{ attrs }}`
- Prefer `<c-*>` usage in page templates; avoid copy-pasting daisyUI markup
  across pages
- Document component inputs and slots in HTML comments at the top of each
  component file
- Use semantic HTML elements inside components for better accessibility

### Best practices

1. **Use `<c-vars />` for defaults and documentation**

   ```django
   {# templates/cotton/button.html #}
   {# Usage: <c-button variant="primary" size="lg">Click me</c-button> #}
   <c-vars variant="primary" size="md" type="button" />
   <button {{ attrs }}
           type="{{ type }}"
           class="btn btn-{{ variant }} btn-{{ size }} {{ attrs.class }}">
       {{ slot }}
   </button>
   ```

2. **Forward HTML attributes with `{{ attrs }}`** Use `{{ attrs }}` to allow
   users to add custom attributes, classes, HTMX directives, etc.:

   ```django
   {# Allows: <c-input name="email" hx-post="/validate" /> #}
   <input {{ attrs }} class="input {{ attrs.class }}" />
   ```

3. **Use named slots for flexible composition**

   ```django
   {# templates/cotton/card.html #}
   <div class="card bg-base-100 shadow-xl">
       <div class="card-body">
           {% if title %}<h2 class="card-title">{{ title }}</h2>{% endif %}
           <div>{{ slot }}</div>
           {% if actions %}
           <div class="card-actions justify-end">{{ actions }}</div>
           {% endif %}
       </div>
   </div>
   ```

   Usage:

   ```django
   <c-card title="Product Name">
       <c-slot name="default">Product description here</c-slot>
       <c-slot name="actions">
           <c-button variant="primary">Buy Now</c-button>
       </c-slot>
   </c-card>
   ```

4. **Use `:attrs` for higher-order components** When building a component that
   wraps another component:

   ```django
   {# templates/cotton/icon-button.html #}
   <c-button :attrs="attrs" class="gap-2">
       <span class="icon">{{ icon }}</span>
       {{ slot }}
   </c-button>
   ```

5. **Use `only` for context isolation** Add `only` to prevent the component from
   seeing parent context, reducing coupling:

   ```django
   <c-card :title="post.title" :content="post.body" only />
   ```

6. **Component file organization**
   - Use snake_case filenames: `button.html`, `alert_banner.html`
   - Call with kebab-case tags: `<c-button>`, `<c-alert-banner>`
   - Use subfolders for namespacing: `forms/text_input.html` →
     `<c-forms.text-input>`
   - Use `index.html` for default exports: `modal/index.html` → `<c-modal>`

### Component examples

```django
{# templates/cotton/input.html #}
{# Usage: <c-input name="email" type="email" class="input-bordered" placeholder="Enter email" /> #}
<input {{ attrs }} class="input {{ attrs.class }}" />
```

```django
{# templates/cotton/button.html #}
{# Usage: <c-button variant="primary" hx-post="/submit">Submit</c-button> #}
<button {{ attrs }} class="btn {{ attrs.class|default:'btn-primary' }}">
    {{ slot }}
</button>
```

```django
{# Usage in templates #}
<c-input name="join_code" inputmode="numeric" class="input-bordered w-full" />
<c-button hx-post="/save" hx-target="#result">Save</c-button>
```

## Template Fragments (Partial Rendering)

For HTMX updates, prefer template fragments over separate “partials-only” files:

- **Django 6.0+**: Use built-in template partials (`{% partialdef %}` /
  `{% partial %}`) to define fragments close to the full-page template. No
  `{% load %}` tag needed.
- Use stable element IDs so HTMX swaps are predictable.
- Keep modal markup in a fragment intended for `#modal-root`.
- Return fragments for HTMX requests, full pages for normal requests.

### When to use template fragments vs Cotton components vs includes

**Template partials (`{% partialdef %}`)** for:

- HTMX-swappable fragments within a single page
- Page-specific logic that won't be reused elsewhere
- Returning fragment-only responses:
  `render(request, 'page.html#fragment', context)`

**Cotton components (`<c-*>`)** for:

- Reusable UI building blocks used across 3+ different templates
- Design system components (buttons, cards, inputs, badges)
- Purely presentational elements with explicit props/slots

**Includes (`{% include 'partials/navbar.html' %}`)** for:

- Static template composition (navbar, footer, sidebar)
- Large templates broken into logical sections
- Non-interactive content that's same across pages

### Template partial pattern (Django 6.0+)

```django
{# user_list.html #}
{% extends "_base.html" %}

{% block content %}
<div id="user-list">
    {% partialdef user_list_content %}
        <ul>
        {% for user in users %}
            <li>{{ user.name }}</li>
        {% endfor %}
        </ul>
    {% endpartialdef %}
</div>
{% endblock %}
```

**Note:** The correct Django 6.0 built-in syntax is
`{% partialdef name %}...{% endpartialdef %}` for definition and
`{% partial name %}` for rendering within the same template. No `{% load %}` tag
is required.

### View pattern for HTMX requests

```python
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

def user_list(request: HttpRequest) -> HttpResponse:
    users = User.objects.all()

    # Return partial for HTMX requests, full page otherwise
    if request.htmx:  # Requires django_htmx.middleware.HtmxMiddleware
        return render(request, 'users/user_list.html#user_list_content', {'users': users})
    return render(request, 'users/user_list.html', {'users': users})
```

## HTMX Integration Patterns

Use HTMX for mutations and fragment updates.

- **CSRF protection**: Set `hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}}'`
  on `<body>` tag globally, or use `{% csrf_token %}` in individual forms.
- **Progressive enhancement**: Forms must work without JavaScript; HTMX enhances
  them.
- **Prefer server-rendered fragments** over client-side rendering.
- **Loading states**: Use `hx-indicator` to show spinners during requests.
- **Scoped swaps**: Use `hx-target` to update specific containers, not entire
  sections.
- **Business logic**: Always enforce rules server-side; HTMX is for UX only.
- **django-htmx middleware**: Add `django_htmx.middleware.HtmxMiddleware` to
  detect HTMX requests via `request.htmx`.

### Base template CSRF setup (django-htmx)

```django
{% load static django_htmx %}
<!DOCTYPE html>
<html lang="en" data-theme="app">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}App{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'css/styles.css' %}">
    {% htmx_script %}
</head>
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}}'>
    {% block content %}{% endblock %}
</body>
</html>
```

### HTMX form patterns

```django
{# Progressive enhancement: works with and without JS #}
<form method="post" action="/search"
      hx-post="/search"
      hx-target="#results"
      hx-trigger="submit"
      hx-indicator="#loading">
    {% csrf_token %}
    <input type="search" name="q" placeholder="Search...">
    <button type="submit" class="btn btn-primary">
        Search
        <span id="loading" class="loading loading-spinner htmx-indicator"></span>
    </button>
</form>

<div id="results">
    {# Results rendered here #}
</div>
```

### HTMX attributes reference

- `hx-get`, `hx-post`, `hx-put`, `hx-delete`: HTTP methods for requests
- `hx-target`: CSS selector for element to update (default: triggering element)
- `hx-swap`: How to swap content (`innerHTML`, `outerHTML`, `beforeend`,
  `afterend`)
- `hx-trigger`: Event that triggers request (default: `click` for buttons,
  `submit` for forms)
- `hx-indicator`: Element to show during request
- `hx-vals`: Add JSON data to request
- `hx-boost`: Enable AJAX for all links/forms in container

## Alpine.js Guidelines (Only Where Needed)

### Component Architecture

- Keep components **small and focused** (one behavior).
- Use `x-data` for local state; use `Alpine.store()` for cross-page concerns
  (toasts, locale UI state).
- Avoid “business logic” in Alpine; Alpine is for UI behavior only.

### Alpine.js Patterns

```html
<!-- Good: Small, focused component -->
<div x-data="{ open: false, loading: false }">
  <button @click="open = !open" :aria-expanded="open">Toggle</button>
  <div x-show="open" x-transition>Content</div>
</div>
```

### Alpine.js Best Practices

- Use `x-cloak` to prevent flash of unstyled content:
  `[x-cloak] { display: none !important; }`
- Prefer `@click` over `x-on:click` for brevity
- Use `:class` for conditional styling: `:class="{ 'active': isActive }"`
- Add `.debounce` for search inputs that trigger HTMX:
  `x-model.debounce.250ms="q"`

## Localization (i18n) UX

- Language selector should be accessible on key pages (landing, settings,
  account).
- Keep strings short; avoid idioms and cultural references.
- Use Django i18n tags (`{% trans %}`, `{% blocktrans %}`) for all user-facing
  text.
- Mark translatable strings in Python with `gettext()` or `gettext_lazy()`.

### Django i18n template patterns

```django
{% load i18n %}

{# Simple translation #}
<h1>{% trans "Welcome" %}</h1>

{# Translation with context #}
<p>{% trans "Home" context "navigation" %}</p>

{# Translation with variables #}
{% blocktrans with name=user.name %}
  Hello, {{ name }}!
{% endblocktrans %}

{# Pluralization #}
{% blocktrans count counter=items|length %}
  There is {{ counter }} item.
{% plural %}
  There are {{ counter }} items.
{% endblocktrans %}
```

## Accessibility Baseline

- **Contrast**: Meet WCAG AA minimum (4.5:1 for normal text, 3:1 for large
  text).
- **Tap targets**: Minimum 44×44px for all interactive elements (buttons, links,
  form controls).
- **Color**: Never rely on color alone; use labels, icons, or text explanations.
- **Semantic HTML**: Use proper elements (`<button>`, `<nav>`, `<main>`) before
  adding ARIA.
- **Keyboard navigation**: All interactive elements must be keyboard accessible
  (test with Tab key).
- **Focus states**: Visible focus indicators on all interactive elements.
- **Alt text**: All images must have descriptive `alt` attributes (empty
  `alt=""` for decorative images).
- **Form labels**: Every input must have an associated `<label>` element.
- **ARIA attributes**: Use `aria-label`, `aria-expanded`, `aria-controls` when
  needed for dynamic content.

### Accessibility patterns

```html
<!-- Accessible form -->
<form>
  <label for="email" class="label">
    <span class="label-text">Email</span>
  </label>
  <input
    type="email"
    id="email"
    name="email"
    class="input input-bordered"
    required
    aria-required="true"
  />

  <button type="submit" class="btn btn-primary">
    <span>Submit</span>
    <span class="sr-only">Submit form</span>
  </button>
</form>

<!-- Accessible toggle -->
<button
  @click="open = !open"
  :aria-expanded="open"
  aria-controls="content"
  class="btn"
>
  Toggle Content
</button>
<div id="content" x-show="open" role="region">Content here</div>

<!-- Screen reader only text -->
<style>
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
  }
</style>
```

## Custom CSS Utilities

The project includes custom animation and styling utilities in
`src/static/css/input.css`. These are opt-in classes to enhance UI polish
without requiring additional dependencies.

### Animation Utilities

**Modal and overlay animations:**

```html
<!-- Modal with enter animation -->
<dialog id="my_modal" class="modal">
  <div class="modal-box animate-modal-enter">
    <h3 class="text-lg font-bold">Modal Title</h3>
    <p>Modal content here.</p>
  </div>
  <form method="dialog" class="modal-backdrop animate-backdrop-enter">
    <button>close</button>
  </form>
</dialog>
```

**Available animation classes:**

- `animate-modal-enter` - Subtle scale + fade-in for modals and popups (0.2s)
- `animate-backdrop-enter` - Fade-in for backdrop overlays (0.15s)
- `animate-slide-down-fade` - Slide down + fade for dropdowns and notices (0.2s)
- `animate-fade-in-up` - Slide up + fade for list items and cards (0.3s)
- `animate-spinner` - Continuous rotation for loading indicators

**Usage patterns:**

```html
<!-- Staggered list animations -->
<ul>
  <li class="animate-fade-in-up" style="animation-delay: 0ms">Item 1</li>
  <li class="animate-fade-in-up" style="animation-delay: 50ms">Item 2</li>
  <li class="animate-fade-in-up" style="animation-delay: 100ms">Item 3</li>
</ul>

<!-- Custom loading spinner -->
<div class="animate-spinner">
  <svg class="h-5 w-5"><!-- icon --></svg>
</div>

<!-- Dropdown with slide animation -->
<div
  x-show="open"
  x-transition:enter="animate-slide-down-fade"
  class="dropdown-content"
>
  Dropdown items
</div>
```

### Skeleton Shimmer Utility

For loading states that need a shimmer effect:

```html
<!-- Skeleton loader with shimmer -->
<div class="skeleton-shimmer h-4 w-32 rounded"></div>
<div class="skeleton-shimmer mt-2 h-8 w-full rounded"></div>

<!-- Card skeleton -->
<div class="card bg-base-100">
  <div class="card-body space-y-3">
    <div class="skeleton-shimmer h-6 w-3/4 rounded"></div>
    <div class="skeleton-shimmer h-4 w-full rounded"></div>
    <div class="skeleton-shimmer h-4 w-5/6 rounded"></div>
  </div>
</div>
```

**Features:**

- Automatically adapts to light/dark themes via `[data-theme='dark']`
- Uses `theme()` function for consistent colors with daisyUI
- 1.5s infinite animation loop

### Focus-Visible Ring

Custom focus indicator aligned to theme colors (automatically applied):

```css
/* Applied globally to all interactive elements */
button:focus-visible,
a:focus-visible,
input:focus-visible,
textarea:focus-visible,
select:focus-visible,
[tabindex]:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px
    color-mix(in oklab, theme(--color-primary) 60%, transparent);
  border-radius: inherit;
}
```

**This replaces the default browser outline with:**

- 2px semi-transparent ring using the primary theme color
- Consistent with daisyUI aesthetic
- Inherits border-radius from element
- Only visible on keyboard focus (`:focus-visible`), not mouse clicks

### Themed Scrollbars

Opt-in custom scrollbars for app regions:

```html
<!-- Main content area with themed scrollbar -->
<main class="app-main-scrollbar overflow-y-auto">
  <!-- Long content -->
</main>

<!-- Sidebar with accent-colored scrollbar -->
<aside class="sidebar-scrollbar overflow-y-auto">
  <!-- Navigation items -->
</aside>
```

**Features:**

- `app-main-scrollbar` - Neutral-colored thin scrollbar (light: neutral-400,
  dark: neutral-600)
- `sidebar-scrollbar` - Primary-colored thin scrollbar (uses theme primary
  color)
- Automatically adapts to light/dark themes
- Uses CSS `scrollbar-width: thin` for Firefox
- Uses `::-webkit-scrollbar-*` pseudo-elements for Chromium browsers
- Transparent track, colored thumb with hover state

**When to use:**

- Long content areas that benefit from visual polish
- Sidebar navigation where brand color reinforces hierarchy
- Skip for short content or mobile views (native overlay scrollbars are better)

### Accessibility Considerations

**Reduced motion:** All animations respect `prefers-reduced-motion` preference
automatically. The project includes a global media query in `input.css` that
reduces animation durations to near-instant for users who prefer reduced motion.

```css
@media (prefers-reduced-motion: reduce) {
  .animate-modal-enter,
  .animate-backdrop-enter,
  .animate-slide-down-fade,
  .animate-fade-in-up {
    animation-duration: 0.01ms !important;
  }
}
```

**For Alpine.js transitions with custom classes:**

```html
<div
  x-show="open"
  x-transition:enter="animate-modal-enter"
  x-transition:enter.duration.0ms.if="window.matchMedia('(prefers-reduced-motion: reduce)').matches"
>
  Content
</div>
```

## Common Patterns to Avoid

- Large client frameworks (React/Vue) or heavy state management.
- Duplicating component markup across pages instead of using Cotton/components.
- Complex, slow animations.
