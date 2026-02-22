---
applyTo: 'src/templates/**/*.html,src/**/templates/**/*.html,src/**/views.py,src/**/urls.py,src/static/js/**/*.js'
---

# HTMX + Cotton + Alpine Patterns

Use these rules for server-rendered interactivity with HTMX, django-cotton
components, and Alpine.js.

## Rendering Strategy

- **Initial loads**: Return full-page templates with complete HTML structure.
- **HTMX requests**: Return focused partial fragments (use `request.htmx` to
  detect).
- **Template organization**: Page shell in `_base.html`, reusable blocks in
  `partials/`, components in `cotton/`.
- **Partial definition**: Use Django 6.0 `{% partialdef %}` or
  `django-template-partials` for fragment rendering.

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
{% load partials %}

{% block content %}
<h1>Items</h1>

<button hx-get="{% url 'items:list' %}"
        hx-target="#item-table"
        hx-swap="outerHTML">
    Refresh List
</button>

{% partialdef item-table inline %}
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

## Best Practices Summary

- **Keep HTMX endpoints in the owning Django app** (follow URL ownership rules).
- **Use `request.htmx` in views** to return partials vs full pages.
- **Leverage django-template-partials** for fragment definitions near full
  templates.
- **Apply CSRF globally** via `hx-headers` in base template.
- **Use explicit swap strategies** (`hx-swap`) for predictable behavior.
- **Add loading indicators** with `hx-indicator` and CSS transitions.
- **Debounce user input** with `hx-trigger="keyup changed delay:500ms"`.
- **Component extraction** when markup repeats across 3+ places.
- **Alpine for UI, HTMX for data** - clear separation of concerns.
- **Progressive enhancement** - forms must work without JavaScript.
