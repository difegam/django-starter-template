---
description: "This file outlines the use of HTMX with django-cotton components and Alpine.js in server-rendered templates. It explains when to opt for Django template partials over cotton components, discusses HTMX attribute patterns, and provides best practices for seamless integration."
applyTo: 'src/templates/**/*.html,src/**/templates/**/*.html,src/**/views.py,src/**/urls.py,src/static/js/**/*.js'
---

# HTMX + Cotton + Alpine Patterns

Use these rules for server-rendered interactivity with HTMX, django-cotton
components, and Alpine.js.

## Mental Model: Partials vs Cotton vs Includes

### Django template partials (Django 6.0+)

Inline, **named** fragments you define with `{% partialdef %}` and render with
`{% partial %}`. They render with the **current template context** and can be
addressed externally via `template.html#partial_name` (e.g., in `render()` or
`{% include %}`).

**Use partials when:**

- The fragment is **only** relevant to one page/template (or one feature
  template) and splitting into a new file would add friction
- You want to return only a fragment for **HTMX/AJAX** by rendering
  `template.html#partial_name`
- The fragment needs page-specific context and logic

### Django Cotton components

File-based **UI components** (templates under `templates/cotton/`) with
**props/attributes**, `{{ slot }}`, **named slots**, dynamic attributes
(`:attr="..."`), attribute forwarding via `{{ attrs }}` / `:attrs`, optional
**context isolation** via `only`, and local defaults via `<c-vars />`.

**Use Cotton components when:**

- The UI piece is reused across 3+ pages (e.g., buttons, inputs, cards, modals)
- You want "component ergonomics": explicit inputs, slots, attribute
  passthrough, default props, and optional context isolation
- Building your design system's reusable building blocks

### Include partials (`{% include 'partials/navbar.html' %}`)

Static template fragments for page composition.

**Use includes when:**

- Breaking large templates into logical sections
- Fragment is same across pages but not interactive
- No HTMX swap targeting needed (e.g., navbar, footer)

**Practical rule:** Partials for local refactors + response fragments, Cotton
for your reusable design system, includes for static composition.

## Rendering Strategy

- **Initial loads**: Return full-page templates with complete HTML structure.
- **HTMX requests**: Return focused partial fragments (use `request.htmx` to
  detect).
- **Template organization**: Page shell in `_base.html`, reusable blocks in
  `partials/`, components in `cotton/`.
- **Partial definition**: Use Django 6.0 built-in `{% partialdef %}` for
  fragment rendering (no package needed; built into Django 6.0+).

### View pattern for partial rendering

```python
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

def item_list(request: HttpRequest) -> HttpResponse:
    items = Item.objects.all()

    # Return partial for HTMX, full page otherwise
    template_name = "items/list.html"
    if request.htmx:
        template_name += "#item-table"  # Render only the partial

    return render(request, template_name, {"items": items})
```

### Template pattern with partials

```django
{% extends "_base.html" %}

{% block content %}
<h1>Items</h1>

<button hx-get="{% url 'items:list' %}"
        hx-target="#item-table"
        hx-swap="outerHTML">
    Refresh List
</button>

{% partialdef item-table %}
<div id="item-table">
    <ul>
    {% for item in items %}
        <li>{{ item.name }}</li>
    {% endfor %}
    </ul>
</div>
{% endpartialdef %}
{% endblock %}
```

**Note:** Django 6.0+ built-in partials don't require `{% load partials %}`. The
`inline` attribute is not part of the standard syntax.

## HTMX Patterns

### Core attributes

- **hx-get/hx-post/hx-put/hx-delete**: HTTP method and endpoint
- **hx-target**: CSS selector for element to update (default: triggering
  element)
- **hx-swap**: How to swap content (see swap strategies below)
- **hx-trigger**: Event that triggers request (default: `click` for buttons,
  `submit` for forms)
- **hx-indicator**: Element to show during request (gets `htmx-request` class)
- **hx-vals**: Add JSON data to request

### Swap strategies

```html
<!-- Replace inner HTML (default) -->
<div hx-get="/content" hx-swap="innerHTML">Replace inner content</div>

<!-- Replace entire element -->
<div hx-get="/content" hx-swap="outerHTML">Replace whole element</div>

<!-- Append to end of children -->
<ul hx-get="/items" hx-swap="beforeend">
  <li>Existing item</li>
  <!-- New items appended here -->
</ul>

<!-- Insert at beginning of children -->
<ul hx-get="/items" hx-swap="afterbegin">
  <!-- New items inserted here -->
  <li>Existing item</li>
</ul>

<!-- Insert after element -->
<div hx-get="/next" hx-swap="afterend">Content</div>
<!-- New content appears here -->

<!-- Insert before element -->
<!-- New content appears here -->
<div hx-get="/prev" hx-swap="beforebegin">Content</div>
```

### Trigger patterns

```html
<!-- Search input with debounce -->
<input
  type="search"
  name="q"
  hx-get="/search"
  hx-trigger="keyup changed delay:500ms, search"
  hx-target="#results"
  hx-sync="this:replace"
  placeholder="Search..."
/>

<!-- Form with inline validation -->
<input
  type="email"
  name="email"
  hx-post="/validate/email"
  hx-trigger="blur changed"
  hx-target="#email-error"
  hx-swap="innerHTML"
/>
<span id="email-error"></span>

<!-- Throttled scroll event -->
<div
  hx-get="/infinite-scroll"
  hx-trigger="scroll throttle:1s"
  hx-target="#content"
  hx-swap="beforeend"
></div>

<!-- Polling for updates -->
<div
  hx-get="/status"
  hx-trigger="every 5s"
  hx-target="this"
  hx-swap="innerHTML"
>
  Checking status...
</div>
```

### Loading states and indicators

```html
<!-- Inline spinner -->
<button hx-post="/submit">
  Submit
  <span class="loading loading-spinner htmx-indicator"></span>
</button>

<!-- External indicator -->
<button hx-post="/submit" hx-indicator="#spinner">Submit</button>
<span id="spinner" class="loading loading-spinner htmx-indicator"></span>

<!-- Disable button during request -->
<button hx-post="/submit" hx-disabled-elt="this">Submit</button>
```

### Required CSS for indicators

```css
/* Hide indicators by default */
.htmx-indicator {
  opacity: 0;
  transition: opacity 200ms ease-in;
}

/* Show when request is in flight */
.htmx-request .htmx-indicator {
  opacity: 1;
}

/* Show when indicator element itself triggers request */
.htmx-request.htmx-indicator {
  opacity: 1;
}
```

### CSRF protection

```django
{# Base template - global CSRF header #}
{% load django_htmx %}
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
    {% block content %}{% endblock %}
</body>

{# Or per-form CSRF token #}
<form hx-post="/submit">
    {% csrf_token %}
    <input type="text" name="data">
    <button type="submit">Submit</button>
</form>
```

### Progressive enhancement pattern

```html
{# Form works with and without JavaScript #}
<form
  method="post"
  action="/items/create"
  hx-post="/items/create"
  hx-target="#item-list"
  hx-swap="beforeend"
>
  {% csrf_token %}
  <input type="text" name="name" required />
  <button type="submit">Add Item</button>
</form>
```

## django-cotton Component Patterns

### Component structure

```django
{# templates/cotton/button.html #}
{# Usage: <c-button variant="primary" hx-post="/action">Submit</c-button> #}
<button {{ attrs }}
        class="btn {{ attrs.class|default:'btn-primary' }}"
        type="{{ type|default:'button' }}">
    {{ slot }}
</button>
```

### Component with HTMX integration

```django
{# templates/cotton/delete-button.html #}
{# Usage: <c-delete-button item-id="123" target="#item-123" /> #}
<button {{ attrs }}
        hx-delete="{% url 'items:delete' item_id=item_id %}"
        hx-target="{{ target }}"
        hx-swap="outerHTML swap:500ms"
        hx-confirm="Are you sure?"
        class="btn btn-error btn-sm">
    <span>Delete</span>
    <span class="loading loading-spinner loading-xs htmx-indicator"></span>
</button>
```

### Component with slots

```django
{# templates/cotton/card.html #}
{# Usage:
    <c-card>
        <c-slot name="title">Card Title</c-slot>
        <c-slot name="content">Card body content</c-slot>
    </c-card>
#}
<div {{ attrs }} class="card bg-base-100 shadow-xl {{ attrs.class }}">
    <div class="card-body">
        {% if title %}
        <h2 class="card-title">{{ title }}</h2>
        {% endif %}
        <div>{{ content }}</div>
    </div>
</div>
```

### HTMX-ready form component

```django
{# templates/cotton/ajax-form.html #}
{# Usage:
    <c-ajax-form action="/submit" target="#result">
        <input name="data">
        <button type="submit">Submit</button>
    </c-ajax-form>
#}
<form {{ attrs }}
      method="{{ method|default:'post' }}"
      action="{{ action }}"
      hx-post="{{ action }}"
      hx-target="{{ target|default:'this' }}"
      hx-swap="{{ swap|default:'innerHTML' }}"
      hx-indicator=".htmx-indicator">
    {% csrf_token %}
    {{ slot }}
</form>
```

## Alpine.js Integration Patterns

### Alpine for UI state, HTMX for server communication

```html
<!-- Good: Alpine manages UI state, HTMX handles server sync -->
<div x-data="{ expanded: false }">
  <button @click="expanded = !expanded" :aria-expanded="expanded" class="btn">
    Toggle Details
  </button>

  <div
    x-show="expanded"
    x-transition
    hx-get="/details/{{ item.id }}"
    hx-trigger="revealed once"
    hx-swap="innerHTML"
  >
    <span class="loading loading-spinner"></span>
  </div>
</div>
```

### Coordinating Alpine with HTMX events

```html
<!-- Update Alpine state based on HTMX events -->
<div x-data="{ saved: false, saving: false }">
  <form
    hx-post="/save"
    @htmx:before-request="saving = true; saved = false"
    @htmx:after-request="saving = false"
    @htmx:response-error="saving = false"
    @htmx:after-settle="saved = true"
  >
    {% csrf_token %}
    <input type="text" name="data" />
    <button type="submit" :disabled="saving">
      <span x-show="!saving">Save</span>
      <span x-show="saving">Saving...</span>
    </button>
  </form>

  <div
    x-show="saved"
    x-transition
    class="alert alert-success"
    x-init="$watch('saved', value => value && setTimeout(() => saved = false, 3000))"
  >
    Saved successfully!
  </div>
</div>
```

### Modal with Alpine + HTMX content loading

```html
<div x-data="{ open: false }">
  <!-- Trigger button -->
  <button @click="open = true" class="btn btn-primary">Open Modal</button>

  <!-- Modal -->
  <div
    x-show="open"
    x-transition
    @click.away="open = false"
    @keydown.escape.window="open = false"
    class="modal modal-open"
    x-cloak
  >
    <div
      class="modal-box animate-modal-enter"
      hx-get="/modal-content"
      hx-trigger="intersect once"
      hx-swap="innerHTML"
    >
      <span class="loading loading-spinner"></span>
    </div>
  </div>
</div>
```

### Native dialog modal with animations

```html
<!-- Trigger button -->
<button onclick="example_modal.showModal()" class="btn btn-primary">
  Open Modal
</button>

<!-- Modal using native dialog element -->
<dialog id="example_modal" class="modal">
  <div class="modal-box animate-modal-enter">
    <h3 class="text-lg font-bold">Modal Title</h3>
    <p class="py-4">Modal content loaded via HTMX on open.</p>
    <div hx-get="/modal-details" hx-trigger="load" hx-swap="innerHTML">
      <span class="loading loading-spinner"></span>
    </div>
    <div class="modal-action">
      <form method="dialog">
        <button class="btn">Close</button>
      </form>
    </div>
  </div>
  <form method="dialog" class="modal-backdrop animate-backdrop-enter">
    <button>close</button>
  </form>
</dialog>
```

## Common Patterns and Anti-Patterns

### ✓ Good Patterns

```html
<!-- Scoped updates -->
<button hx-post="/vote" hx-target="#vote-count" hx-swap="innerHTML">
  Vote
</button>
<span id="vote-count">{{ votes }}</span>

<!-- Stable IDs for predictable swaps -->
<div id="comment-list">
  {% for comment in comments %}
  <div id="comment-{{ comment.id }}">...</div>
  {% endfor %}
</div>

<!-- Progressive enhancement -->
<a href="/details" hx-get="/details" hx-target="#main" hx-push-url="true">
  View Details
</a>
```

### ✗ Anti-Patterns to Avoid

```html
<!-- Don't replace entire app shell -->
<div hx-get="/page" hx-target="body" hx-swap="innerHTML">Bad</div>

<!-- Don't use HTMX for client-only state -->
<button hx-get="/toggle-state">Use Alpine instead</button>

<!-- Don't skip stable IDs -->
<div hx-get="/items" hx-swap="innerHTML">
  <!-- No ID = unpredictable swap behavior -->
</div>

<!-- Don't forget CSRF on mutations -->
<form hx-post="/delete"><!-- Missing {% csrf_token %} --></form>
```

## Best Practices for Django Template Partials

1. **Treat `{% partial %}` as "same-template only"** Define and render within
   the same template. To reuse across files, reference it as `other.html#name`
   via `{% include %}` or `render()` rather than expecting `{% partial name %}`
   to "import" it.

2. **Make dependencies explicit with `{% with %}`** Partials inherit the current
   context, which is convenient but can create hidden coupling. Wrap calls with
   `{% with %}` to document required variables:

   ```django
   {% with user=request.user items=item_list %}
     {% partial user_info %}
   {% endwith %}
   ```

3. **Use `template.html#partial` for HTMX endpoints** Return only the fragment
   you need from the view (cleaner than duplicating mini-templates):

   ```python
   # views.py
   return render(request, "authors.html#user-info", {"user": user})
   ```

4. **Use stable element IDs** Always include a unique ID on the root element of
   fragments for predictable HTMX swapping.

## Best Practices for Django Cotton Components

1. **Adopt a predictable component layout + naming**
   - Put components under `templates/cotton/` (configurable)
   - Use snake_case filenames by default; call components in templates with
     kebab-case tag names
   - Use subfolders with dot notation; use `index.html` as the "default"
     component for a folder when it has sub-components

2. **Prefer explicit inputs; use `<c-vars />` for defaults**
   - Declare defaults (and effectively "document props") at the top of a
     component with `<c-vars />`:

   ```django
   {# templates/cotton/button.html #}
   <c-vars variant="primary" size="md" />
   <button {{ attrs }} class="btn btn-{{ variant }} btn-{{ size }}">
       {{ slot }}
   </button>
   ```

   - Use dynamic attributes (`:attr="..."`) for non-string types and
     "pass-through objects"

3. **Forward HTML attributes intentionally**
   - Use `{{ attrs }}` when your component wraps a real HTML element (especially
     form controls)
   - Use `:attrs="attrs"` to build wrapper/higher-order components that proxy
     all attributes to an inner component:

   ```django
   {# templates/cotton/fancy-button.html #}
   <c-button :attrs="attrs" class="fancy-style">
       <span class="icon">✨</span>
       {{ slot }}
   </c-button>
   ```

4. **Use `only` when you want safety/encapsulation**
   - Add `only` to prevent the component from seeing parent context except for
     passed attributes—this reduces accidental coupling and name collisions:

   ```django
   {# Usage #}
   <c-card :title="post.title" only>{{ post.content }}</c-card>
   ```

5. **Keep components purely presentational**
   - No DB queries, no business logic
   - Accept all data as attributes/slots
   - Minimal branching logic

## Combining Partials and Cotton Cleanly

### Pattern A: Partials inside a page template; Cotton for shared UI primitives

- Page template defines partials like `results_list`, `results_rows`,
  `empty_state`
- Those partials _use_ Cotton components like `<c-table>`, `<c-badge>`,
  `<c-button>`

Example:

```django
{# search.html #}
{% extends "_base.html" %}

{% block content %}
<div id="search-results">
    {% partialdef results_list %}
        <ul>
        {% for result in results %}
            <li>
                <c-badge variant="primary">{{ result.category }}</c-badge>
                {{ result.title }}
            </li>
        {% endfor %}
        </ul>
    {% endpartialdef %}
</div>
{% endblock %}
```

### Pattern B: Partials inside a Cotton component to reduce repetition

A Cotton component is still just a Django template file, so you can use
`{% partialdef %}` inside it to keep internal markup DRY (e.g., a repeated "row"
structure). Partials will render with that component's context.

### Pattern C: Feature template as a "partial library"

Put multiple `{% partialdef %}` blocks into `features/search.html`, then:

- Full page renders normal template
- HTMX endpoints return `features/search.html#results_rows`

This keeps feature fragments co-located:

```python
# views.py
def search_results(request: HttpRequest) -> HttpResponse:
    query = request.GET.get('q', '')
    results = search(query)

    if request.htmx:
        return render(request, 'features/search.html#results_rows', {'results': results})
    return render(request, 'features/search.html', {'results': results})
```

## Best Practices Summary

- **Keep HTMX endpoints in the owning Django app** (follow URL ownership rules).
- **Use `request.htmx` in views** to return partials vs full pages.
- **Use Django 6.0+ built-in `{% partialdef %}`** for fragment definitions near
  full templates (no package needed).
- **Apply CSRF globally** via `hx-headers` in base template.
- **Use explicit swap strategies** (`hx-swap`) for predictable behavior.
- **Add loading indicators** with `hx-indicator` and CSS transitions.
- **Debounce user input** with `hx-trigger="keyup changed delay:500ms"`.
- **Component extraction** when markup repeats across 3+ places.
- **Alpine for UI, HTMX for data** - clear separation of concerns.
- **Progressive enhancement** - forms must work without JavaScript.
- **Decision framework**: Partials for page-local fragments, Cotton for
  cross-app reusable UI, includes for static composition.
