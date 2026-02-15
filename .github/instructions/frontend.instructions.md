---
description: 'frontend patterns (Django templates + HTMX + django-cotton + Alpine + Tailwind/daisyUI)'
applyTo: 'src/**/templates/**/*.html,src/**/static/**/*,src/templates/**/*.html,src/static/**/*'
---

# Frontend Development Guide

Frontend development for this project is **server-rendered first** (Django templates) with **HTMX** for partial updates, **django-cotton** for reusable template components, **Alpine** for lightweight interactivity, and **Tailwind + daisyUI** for a consistent premium UI.

## Technology Stack Overview

- **Django templates**: server-side rendering with `extends` + `{% block %}`
- **django-cotton**: reusable UI components in `templates/cotton/` with `<c-*>` syntax
- **HTMX (+ django-htmx)**: progressive enhancement via HTML attributes + HTMX-aware server responses
- **Alpine.js**: small interactive behaviors (modals, toasts, pickers, micro-interactions)
- **Tailwind CSS + daisyUI**: utility-first + component classes; use custom themes `project` / `project-dark`

## General Frontend Principles

- **Progressive enhancement**: pages must work as normal HTML; HTMX/Alpine only enhance.
- **Mobile-first**: default layouts and touch targets for phones; enhance for desktop/TV.
- **Consistency**: use the shared component library (Cotton/components/partials) instead of one-off markup.
- **Accessibility**: minimum WCAG AA contrast, keyboard support, and clear focus states.

## Project Structure (Frontend Files)

- Templates live under `src/templates/` (project-wide) and `src/<app>/templates/<app>/` (app-owned, namespaced to avoid collisions).
- Static assets live under `src/static/` (project-wide) and `src/<app>/static/<app>/` (app-owned, namespaced).
- Cotton components should live under `src/templates/cotton/` (or app-level `templates/cotton/`) so they can be used everywhere.
- Base template: `src/templates/_base.html` loads static assets, HTMX, Alpine, and defines standard blocks.
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

- Use daisyUI component classes (`btn`, `card`, `badge`, `navbar`, etc.) with Tailwind utilities for layout.
- Implement and use a custom daisyUI theme:
  - Light: `<project-name>` (e.g., `app`)
  - Dark: `<project-name>-dark` (e.g., `app-dark`)
- Prefer setting the theme via `data-theme` (e.g., `<html data-theme="app">`), and keep dark mode as a theme switch (not a separate CSS system).
- Typography: prefer **Inter** (or system fallback).
- Interaction constraints: animations should be subtle and fast; avoid complex motion.

## django-cotton Component Guidelines

Prefer Cotton for shared UI building blocks (buttons, inputs, chips, cards, modal shells).

- Keep components **purely presentational** (no DB queries; minimal branching).
- Expose customization via attributes, and allow pass-through HTML attributes via `{{ attrs }}`.
- Prefer `<c-*>` usage in page templates; avoid copy-pasting daisyUI markup across pages.
- Document component inputs and slots in HTML comments at the top of each component file.
- Use semantic HTML elements inside components for better accessibility.

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

- **Django 6.0+**: Use built-in template partials (`{% partialdef %}` / `{% partial %}`) to define fragments close to the full-page template.
- **Django < 6.0**: Use `django-template-partials` package to provide the same syntax.
- Use stable element IDs so HTMX swaps are predictable.
- Keep modal markup in a fragment intended for `#modal-root`.
- Return fragments for HTMX requests, full pages for normal requests.

### Template partial pattern (Django 6.0+)

```django
{# user_list.html #}
{% extends "_base.html" %}

{% block content %}
<div id="user-list">
    {% partial user_list_content %}
        <ul>
        {% for user in users %}
            <li>{{ user.name }}</li>
        {% endfor %}
        </ul>
    {% endpartial %}
</div>
{% endblock %}
```

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

- **CSRF protection**: Set `hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}}'` on `<body>` tag globally, or use `{% csrf_token %}` in individual forms.
- **Progressive enhancement**: Forms must work without JavaScript; HTMX enhances them.
- **Prefer server-rendered fragments** over client-side rendering.
- **Loading states**: Use `hx-indicator` to show spinners during requests.
- **Scoped swaps**: Use `hx-target` to update specific containers, not entire sections.
- **Business logic**: Always enforce rules server-side; HTMX is for UX only.
- **django-htmx middleware**: Add `django_htmx.middleware.HtmxMiddleware` to detect HTMX requests via `request.htmx`.

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
- `hx-swap`: How to swap content (`innerHTML`, `outerHTML`, `beforeend`, `afterend`)
- `hx-trigger`: Event that triggers request (default: `click` for buttons, `submit` for forms)
- `hx-indicator`: Element to show during request
- `hx-vals`: Add JSON data to request
- `hx-boost`: Enable AJAX for all links/forms in container

## Alpine.js Guidelines (Only Where Needed)

### Component Architecture

- Keep components **small and focused** (one behavior).
- Use `x-data` for local state; use `Alpine.store()` for cross-page concerns (toasts, locale UI state).
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

- Use `x-cloak` to prevent flash of unstyled content: `[x-cloak] { display: none !important; }`
- Prefer `@click` over `x-on:click` for brevity
- Use `:class` for conditional styling: `:class="{ 'active': isActive }"`
- Add `.debounce` for search inputs that trigger HTMX: `x-model.debounce.250ms="q"`

## Localization (i18n) UX

- Language selector should be accessible on key pages (landing, settings, account).
- Keep strings short; avoid idioms and cultural references.
- Use Django i18n tags (`{% trans %}`, `{% blocktrans %}`) for all user-facing text.
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

- **Contrast**: Meet WCAG AA minimum (4.5:1 for normal text, 3:1 for large text).
- **Tap targets**: Minimum 44×44px for all interactive elements (buttons, links, form controls).
- **Color**: Never rely on color alone; use labels, icons, or text explanations.
- **Semantic HTML**: Use proper elements (`<button>`, `<nav>`, `<main>`) before adding ARIA.
- **Keyboard navigation**: All interactive elements must be keyboard accessible (test with Tab key).
- **Focus states**: Visible focus indicators on all interactive elements.
- **Alt text**: All images must have descriptive `alt` attributes (empty `alt=""` for decorative images).
- **Form labels**: Every input must have an associated `<label>` element.
- **ARIA attributes**: Use `aria-label`, `aria-expanded`, `aria-controls` when needed for dynamic content.

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

## Common Patterns to Avoid

- Large client frameworks (React/Vue) or heavy state management.
- Duplicating component markup across pages instead of using Cotton/components.
- Complex, slow animations.
