# Skill: ai.chatkit.widgets

Build rich interactive UI components for ChatKit chatbots using OpenAI's widget system. Use for creating cards, forms, lists, buttons, charts, or any custom UI elements within chat conversations.

## Overview

Widgets are JSON structures rendered as UI components in ChatKit. They consist of:

- **WidgetRoot** - Single container defining the widget structure
- **WidgetNode** - Individual components (text, buttons, images, forms, etc.)

## Basic Widget Structure

```json
{
  "type": "card",
  "id": "widget_1",
  "children": [
    {
      "type": "text",
      "id": "text_1",
      "value": "Hello from a widget!"
    }
  ]
}
```

---

## Quick Start: Common Widget Patterns

### Pattern 1: Information Card

```json
{
  "type": "card",
  "id": "info_card",
  "status": "success",
  "statusText": "Completed",
  "children": [
    {
      "type": "headline",
      "id": "title",
      "value": "Order Confirmed",
      "size": "large"
    },
    {
      "type": "text",
      "id": "description",
      "value": "Your order #12345 has been confirmed and will ship soon."
    },
    {
      "type": "divider",
      "id": "div1"
    },
    {
      "type": "button",
      "id": "track_btn",
      "label": "Track Order",
      "action": {
        "type": "track_order",
        "payload": {"order_id": "12345"}
      }
    }
  ]
}
```

### Pattern 2: Form Widget

```json
{
  "type": "form",
  "id": "contact_form",
  "onSubmitAction": {
    "type": "submit_contact",
    "handler": "server"
  },
  "children": [
    {
      "type": "label",
      "id": "name_label",
      "value": "Name"
    },
    {
      "type": "input",
      "id": "name_input",
      "placeholder": "Enter your name"
    },
    {
      "type": "label",
      "id": "email_label",
      "value": "Email"
    },
    {
      "type": "input",
      "id": "email_input",
      "inputType": "email",
      "placeholder": "Enter your email"
    },
    {
      "type": "button",
      "id": "submit_btn",
      "label": "Submit",
      "variant": "primary"
    }
  ]
}
```

### Pattern 3: List with Actions

```json
{
  "type": "list",
  "id": "product_list",
  "children": [
    {
      "type": "list-item",
      "id": "item_1",
      "children": [
        {
          "type": "column",
          "id": "col_1",
          "children": [
            {
              "type": "text",
              "id": "product_name",
              "value": "Premium Widget",
              "weight": "bold"
            },
            {
              "type": "text",
              "id": "product_price",
              "value": "$29.99"
            }
          ]
        },
        {
          "type": "button",
          "id": "add_btn",
          "label": "Add to Cart",
          "size": "small",
          "action": {
            "type": "add_to_cart",
            "payload": {"product_id": "widget_1"}
          }
        }
      ]
    }
  ]
}
```

---

## Widget Components Reference

### Container Components

**Card** - Primary container with optional status indicator
```json
{
  "type": "card",
  "status": "success|warning|error|info",
  "statusText": "Optional status label",
  "children": [...]
}
```

**Column** - Vertical flex container
```json
{
  "type": "column",
  "gap": "small|medium|large",
  "children": [...]
}
```

**Row** - Horizontal flex container
```json
{
  "type": "row",
  "gap": "small|medium|large",
  "children": [...]
}
```

**List** - Scrollable list container
```json
{
  "type": "list",
  "children": [/* list-item components */]
}
```

**Form** - Form container with submit action
```json
{
  "type": "form",
  "onSubmitAction": {...},
  "children": [...]
}
```

### Text Components

**Headline** - Prominent header text
```json
{
  "type": "headline",
  "value": "Header Text",
  "size": "small|medium|large"
}
```

**Text** - Body text with formatting
```json
{
  "type": "text",
  "value": "Content text",
  "weight": "normal|bold",
  "style": "normal|italic",
  "align": "left|center|right"
}
```

**Caption** - Small supplementary text
```json
{
  "type": "caption",
  "value": "Subtitle or metadata"
}
```

### Input Components

**Input** - Single-line text input
```json
{
  "type": "input",
  "id": "unique_id",
  "placeholder": "Enter text...",
  "inputType": "text|email|number|tel|url",
  "value": "Default value"
}
```

**Textarea** - Multi-line text input
```json
{
  "type": "textarea",
  "id": "unique_id",
  "placeholder": "Enter message...",
  "rows": 4
}
```

**Checkbox** - Boolean input
```json
{
  "type": "checkbox",
  "id": "unique_id",
  "label": "I agree to terms",
  "checked": false
}
```

**Date Picker** - Date selection
```json
{
  "type": "date-picker",
  "id": "unique_id",
  "value": "2025-01-15"
}
```

### Interactive Components

**Button** - Action trigger
```json
{
  "type": "button",
  "id": "unique_id",
  "label": "Click Me",
  "variant": "primary|secondary|danger",
  "size": "small|medium|large",
  "action": {
    "type": "custom_action",
    "handler": "server|client",
    "payload": {...}
  }
}
```

**Badge** - Status indicator
```json
{
  "type": "badge",
  "value": "New",
  "variant": "success|warning|error|info"
}
```

### Media Components

**Image** - Display images
```json
{
  "type": "image",
  "id": "unique_id",
  "url": "https://example.com/image.jpg",
  "alt": "Description",
  "fit": "cover|contain|fill",
  "width": "100px",
  "height": "100px"
}
```

**Icon** - Built-in icons
```json
{
  "type": "icon",
  "name": "check|alert|info|error|calendar|location|person",
  "size": "small|medium|large"
}
```

**Chart** - Data visualization
```json
{
  "type": "chart",
  "chartType": "bar|line|area",
  "data": [
    {"x": "Jan", "y": 100},
    {"x": "Feb", "y": 150}
  ]
}
```

### Layout Components

**Divider** - Visual separator
```json
{
  "type": "divider"
}
```

**Label** - Form field label
```json
{
  "type": "label",
  "value": "Field Name",
  "for": "input_id"
}
```

---

## Action Handling

### Server-Side Actions

Actions processed on backend with full context:

```python
from chatkit import ChatKitServer
from chatkit.events import stream_widget

class MyChatKitServer(ChatKitServer):
    async def action(self, action_type: str, payload: dict, context: Any):
        """Handle widget actions"""

        if action_type == "add_to_cart":
            product_id = payload.get("product_id")
            result = await add_to_cart(product_id, context.user_id)

            # Return confirmation widget
            widget = {
                "type": "card",
                "children": [{
                    "type": "text",
                    "value": f"Added {result.product_name} to cart!"
                }]
            }

            async for event in stream_widget(thread, widget, generate_id):
                yield event
```

### Client-Side Actions

Actions handled in JavaScript:

```javascript
chatkit.setOptions({
  widgets: {
    async onAction(action, item) {
      if (action.type === 'open_url') {
        window.open(action.payload.url, '_blank');
      } else if (action.type === 'copy_text') {
        await navigator.clipboard.writeText(action.payload.text);
        alert('Copied!');
      }
      // Forward to server for additional processing
      await fetch('/api/widget-action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, itemId: item.id })
      });
    }
  }
});
```

---

## Python Widget Builder

```python
from typing import List, Dict, Any, Optional


class WidgetBuilder:
    """Helper class to build ChatKit widgets"""

    @staticmethod
    def card(
        id: str,
        children: List[Dict],
        status: Optional[str] = None,
        status_text: Optional[str] = None
    ) -> Dict:
        """Create a card widget"""
        widget = {
            "type": "card",
            "id": id,
            "children": children
        }
        if status:
            widget["status"] = status
        if status_text:
            widget["statusText"] = status_text
        return widget

    @staticmethod
    def text(
        id: str,
        value: str,
        weight: str = "normal",
        align: str = "left"
    ) -> Dict:
        """Create a text component"""
        return {
            "type": "text",
            "id": id,
            "value": value,
            "weight": weight,
            "align": align
        }

    @staticmethod
    def headline(id: str, value: str, size: str = "medium") -> Dict:
        """Create a headline component"""
        return {
            "type": "headline",
            "id": id,
            "value": value,
            "size": size
        }

    @staticmethod
    def button(
        id: str,
        label: str,
        action_type: str,
        payload: Dict = None,
        variant: str = "primary",
        handler: str = "server"
    ) -> Dict:
        """Create a button component"""
        return {
            "type": "button",
            "id": id,
            "label": label,
            "variant": variant,
            "action": {
                "type": action_type,
                "handler": handler,
                "payload": payload or {}
            }
        }

    @staticmethod
    def input_field(
        id: str,
        placeholder: str = "",
        input_type: str = "text",
        value: str = ""
    ) -> Dict:
        """Create an input field"""
        return {
            "type": "input",
            "id": id,
            "placeholder": placeholder,
            "inputType": input_type,
            "value": value
        }

    @staticmethod
    def form(
        id: str,
        children: List[Dict],
        submit_action: str,
        handler: str = "server"
    ) -> Dict:
        """Create a form widget"""
        return {
            "type": "form",
            "id": id,
            "onSubmitAction": {
                "type": submit_action,
                "handler": handler
            },
            "children": children
        }

    @staticmethod
    def list_widget(id: str, items: List[Dict]) -> Dict:
        """Create a list widget"""
        return {
            "type": "list",
            "id": id,
            "children": [
                {"type": "list-item", "id": f"{id}_item_{i}", "children": [item]}
                for i, item in enumerate(items)
            ]
        }

    @staticmethod
    def image(
        id: str,
        url: str,
        alt: str = "",
        width: str = "auto",
        height: str = "auto"
    ) -> Dict:
        """Create an image component"""
        return {
            "type": "image",
            "id": id,
            "url": url,
            "alt": alt,
            "width": width,
            "height": height
        }

    @staticmethod
    def divider(id: str) -> Dict:
        """Create a divider"""
        return {"type": "divider", "id": id}

    @staticmethod
    def column(id: str, children: List[Dict], gap: str = "medium") -> Dict:
        """Create a column layout"""
        return {
            "type": "column",
            "id": id,
            "gap": gap,
            "children": children
        }

    @staticmethod
    def row(id: str, children: List[Dict], gap: str = "medium") -> Dict:
        """Create a row layout"""
        return {
            "type": "row",
            "id": id,
            "gap": gap,
            "children": children
        }
```

---

## Common Widget Templates

### Confirmation Dialog

```python
def create_confirmation_widget(
    title: str,
    message: str,
    confirm_action: str,
    cancel_action: str = None
) -> Dict:
    builder = WidgetBuilder()

    buttons = [
        builder.button("confirm", "Confirm", confirm_action, variant="primary")
    ]
    if cancel_action:
        buttons.append(
            builder.button("cancel", "Cancel", cancel_action, variant="secondary")
        )

    return builder.card(
        "confirmation",
        children=[
            builder.headline("title", title),
            builder.text("message", message),
            builder.divider("div1"),
            builder.row("actions", buttons, gap="small")
        ]
    )
```

### Status Notification

```python
def create_status_widget(
    status: str,  # "success", "warning", "error", "info"
    title: str,
    message: str,
    actions: List[Dict] = None
) -> Dict:
    builder = WidgetBuilder()

    children = [
        builder.headline("title", title),
        builder.text("message", message)
    ]

    if actions:
        children.append(builder.divider("div1"))
        children.append(
            builder.row(
                "actions",
                [builder.button(**action) for action in actions],
                gap="small"
            )
        )

    return builder.card(
        "status_widget",
        children=children,
        status=status,
        status_text=status.capitalize()
    )
```

### Dynamic Form

```python
def create_form_widget(
    title: str,
    fields: List[Dict[str, str]],  # {"label": "Name", "id": "name", "type": "text"}
    submit_action: str
) -> Dict:
    builder = WidgetBuilder()

    form_children = [builder.headline("form_title", title)]

    for field in fields:
        form_children.append(
            builder.text(f"{field['id']}_label", field["label"], weight="bold")
        )
        form_children.append(
            builder.input_field(
                field["id"],
                placeholder=field.get("placeholder", ""),
                input_type=field.get("type", "text")
            )
        )

    form_children.append(
        builder.button("submit", "Submit", submit_action, variant="primary")
    )

    return builder.form("form_widget", form_children, submit_action)
```

---

## Template Examples

### Product Card

```json
{
  "type": "card",
  "id": "product_card",
  "children": [
    {
      "type": "image",
      "id": "product_img",
      "url": "https://example.com/product.jpg",
      "alt": "Product Name",
      "height": "200px",
      "fit": "cover"
    },
    {
      "type": "headline",
      "id": "product_name",
      "value": "Premium Widget Pro",
      "size": "medium"
    },
    {
      "type": "row",
      "id": "price_row",
      "children": [
        {
          "type": "text",
          "id": "price",
          "value": "$99.99",
          "weight": "bold"
        },
        {
          "type": "badge",
          "id": "discount",
          "value": "20% OFF",
          "variant": "success"
        }
      ]
    },
    {
      "type": "divider",
      "id": "div1"
    },
    {
      "type": "row",
      "id": "actions",
      "gap": "small",
      "children": [
        {
          "type": "button",
          "id": "add_cart",
          "label": "Add to Cart",
          "variant": "primary",
          "action": {
            "type": "add_to_cart",
            "payload": {"product_id": "widget_pro"}
          }
        },
        {
          "type": "button",
          "id": "wishlist",
          "label": "Save",
          "variant": "secondary",
          "action": {
            "type": "add_to_wishlist",
            "payload": {"product_id": "widget_pro"}
          }
        }
      ]
    }
  ]
}
```

### Appointment Confirmation

```json
{
  "type": "card",
  "id": "appointment_card",
  "status": "success",
  "statusText": "Confirmed",
  "children": [
    {
      "type": "headline",
      "id": "title",
      "value": "Appointment Confirmed"
    },
    {
      "type": "column",
      "id": "details",
      "gap": "medium",
      "children": [
        {
          "type": "row",
          "id": "date_row",
          "children": [
            {"type": "icon", "id": "calendar_icon", "name": "calendar"},
            {
              "type": "column",
              "id": "date_info",
              "children": [
                {
                  "type": "text",
                  "id": "date",
                  "value": "Wednesday, January 15, 2025",
                  "weight": "bold"
                },
                {"type": "caption", "id": "time", "value": "3:00 PM - 4:00 PM"}
              ]
            }
          ]
        },
        {
          "type": "row",
          "id": "location_row",
          "children": [
            {"type": "icon", "id": "location_icon", "name": "location"},
            {"type": "text", "id": "location", "value": "123 Main St, Suite 100"}
          ]
        }
      ]
    },
    {"type": "divider", "id": "div1"},
    {
      "type": "row",
      "id": "actions",
      "gap": "small",
      "children": [
        {
          "type": "button",
          "id": "add_calendar",
          "label": "Add to Calendar",
          "variant": "primary",
          "action": {"type": "add_to_calendar", "payload": {"appointment_id": "apt_123"}}
        },
        {
          "type": "button",
          "id": "reschedule",
          "label": "Reschedule",
          "variant": "secondary",
          "action": {"type": "reschedule", "payload": {"appointment_id": "apt_123"}}
        }
      ]
    }
  ]
}
```

### Statistics Dashboard

```json
{
  "type": "card",
  "id": "stats_dashboard",
  "children": [
    {"type": "headline", "id": "title", "value": "Performance Overview"},
    {
      "type": "row",
      "id": "metrics",
      "gap": "large",
      "children": [
        {
          "type": "column",
          "id": "metric1",
          "children": [
            {"type": "headline", "id": "metric1_value", "value": "1,234", "size": "large"},
            {"type": "caption", "id": "metric1_label", "value": "Total Users"}
          ]
        },
        {
          "type": "column",
          "id": "metric2",
          "children": [
            {"type": "headline", "id": "metric2_value", "value": "89%", "size": "large"},
            {"type": "caption", "id": "metric2_label", "value": "Satisfaction"}
          ]
        },
        {
          "type": "column",
          "id": "metric3",
          "children": [
            {"type": "headline", "id": "metric3_value", "value": "$45K", "size": "large"},
            {"type": "caption", "id": "metric3_label", "value": "Revenue"}
          ]
        }
      ]
    },
    {"type": "divider", "id": "div1"},
    {
      "type": "chart",
      "id": "growth_chart",
      "chartType": "line",
      "data": [
        {"x": "Jan", "y": 100},
        {"x": "Feb", "y": 150},
        {"x": "Mar", "y": 200},
        {"x": "Apr", "y": 180},
        {"x": "May", "y": 250}
      ]
    }
  ]
}
```

---

## Streaming Widget Updates

### Progressive Widget Building

```python
async def respond(self, thread, input, context):
    # Create initial widget
    widget = Card(id="progress", children=[
        Text(id="status", value="Processing...")
    ])

    # Stream initial widget
    async for event in stream_widget(thread, widget, generate_id):
        yield event

    # Process data
    result = await process_data()

    # Update widget with results
    widget.children.append(
        Text(id="result", value=f"Completed: {result}")
    )

    # Stream updated widget
    async for event in stream_widget(thread, widget, generate_id):
        yield event
```

### Progress Updates

```python
from chatkit.events import ProgressUpdateEvent

async def long_running_task(self, thread):
    yield ProgressUpdateEvent(message="Searching database...", progress=0.3)
    results = await search_database()

    yield ProgressUpdateEvent(message="Analyzing results...", progress=0.7)
    analysis = await analyze(results)

    # Return final widget
    widget = create_results_widget(analysis)
    async for event in stream_widget(thread, widget, generate_id):
        yield event
```

---

## Best Practices

**Widget Design**
- Keep widgets focused on single tasks
- Use consistent styling across widgets
- Provide clear action buttons
- Include helpful error states
- Make widgets mobile-responsive

**Performance**
- Limit widget complexity (avoid 100+ components)
- Avoid deeply nested structures
- Stream large widgets progressively
- Cache widget templates

**Accessibility**
- Include alt text for images
- Use semantic HTML structure
- Provide keyboard navigation
- Include ARIA labels where needed

**User Experience**
- Provide immediate feedback on actions
- Show loading states
- Handle errors gracefully
- Make actions reversible when possible

**Consistent IDs**
- Use descriptive IDs that indicate purpose
- Ensure all IDs are unique within a widget
- Follow naming convention: `{purpose}_{type}` (e.g., `submit_btn`, `name_input`)

---

## Resources

**Widget Builder**: https://widgets.chatkit.studio/
- Design visually with drag and drop
- Preview live updates
- Copy generated JSON
- Customize properties and styling

## Related Skills

- `ai.chatkit.backend` - Backend ChatKit server implementation
- `ai.chatkit.frontend` - Frontend ChatKit integration
