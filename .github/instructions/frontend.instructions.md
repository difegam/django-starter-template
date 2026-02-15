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
- **Tailwind CSS + daisyUI**: utility-first + component classes; use custom themes `qjam` / `qjam-dark`

## General Frontend Principles

- **Progressive enhancement**: pages must work as normal HTML; HTMX/Alpine only enhance.
- **Mobile-first**: default layouts and touch targets for phones; enhance for desktop/TV.
- **Consistency**: use the shared component library (Cotton/components/partials) instead of one-off markup.
- **Accessibility**: minimum WCAG AA contrast, keyboard support, and clear focus states.

## Project Structure (Frontend Files)

- Templates live under `src/templates/` (project-wide) and `src/<app>/templates/` (app-owned).
- Static assets live under `src/static/` (project-wide) and `src/<app>/static/` (app-owned).
- Cotton components should live under `src/templates/cotton/` (or app-level `templates/cotton/`) so they can be used everywhere.

## Theme & UI System (Premium Layout)

- Use daisyUI component classes (`btn`, `card`, `badge`, `navbar`, etc.) with Tailwind utilities for layout.
- Implement and use a custom daisyUI theme:
  - Light: `<project-name>` (e.g., `app`)
  - Dark: `<project-name>-dark` (e.g., `app-dark`)
- Prefer setting the theme via `data-theme` (e.g., `<html data-theme="app">`), and keep dark mode as a theme switch (not a separate CSS system).
- Typography: prefer **Inter** (or system fallback).
- Interaction constraints: animations should be subtle and fast; avoid complex motion.

## django-cotton Component Guidelines

Prefer Cotton for shared UI building blocks (buttons, inputs, chips, track cards, modal shell).

- Keep components **purely presentational** (no DB queries; minimal branching).
- Expose customization via attributes, and allow pass-through HTML attributes via `{{ attrs }}`.
- Prefer `<c-*>` usage in page templates; avoid copy-pasting daisyUI markup across pages.

Example:

```django
{# templates/cotton/input.html #}
<input type="text" {{ attrs }} />
```

```django
<c-input name="join_code" inputmode="numeric" class="input input-bordered w-full" />
```

## Template Fragments (Partial Rendering)

For HTMX updates, prefer template fragments over separate “partials-only” files:

- Prefer Django 6.0 template partials (`{% partialdef %}` / `{% partial %}`) to define fragments close to the full-page template.
- If the project stays on Django < 6.0, use `django-template-partials` to provide the same syntax.
- Use stable element IDs so HTMX swaps are predictable.
- Keep modal markup in a fragment intended for `#modal-root`.

## HTMX Integration Patterns

Use HTMX for mutations and fragment updates.

- Always include `{% csrf_token %}` on `hx-post`/`hx-delete`/`hx-put` forms.
- Prefer server-rendered fragments over client-side rendering.
- Use `hx-indicator` for loading states and keep swaps scoped (`hx-target` to a small container).
- Don’t depend on HTMX to enforce business rules (e.g., Top-3 voting) — render disabled states, but enforce server-side.

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

Per the premium layout spec:

- Language selector is always available on landing/join/session pages.
- Keep strings short; avoid idioms.
- Use Django i18n tags (`{% trans %}`, `{% blocktrans %}`) for user-facing text.

## Accessibility Baseline

- Contrast: meet WCAG AA for text.
- Tap targets: ≥ 44px for all primary actions.
- Never rely on color alone (e.g., Top-3 votable tracks must be labeled/disabled with an explanation).
- Prefer semantic HTML before adding ARIA.

## Common Patterns to Avoid

- Large client frameworks (React/Vue) or heavy state management.
- Duplicating component markup across pages instead of using Cotton/components.
- Complex, slow animations.
