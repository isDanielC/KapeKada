from pyscript import document, window
from pyodide.ffi import create_proxy
from datetime import datetime

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

DRINK_PRICES = {
    "americano": ("Americano", 40),
    "cappuccino": ("Cappuccino", 49),
    "mocha": ("Mocha", 52),
    "caramel_macchiato": ("Caramel Macchiato", 55),
    "iced_spanish_latte": ("Iced Spanish Latte", 55),
    "matcha_latte": ("Matcha Latte", 58),
}

SIZE_SURCHARGE = {"regular": 0, "large": 10}

ADDON_PRICES = {
    "addon-shot": ("Extra Shot", 15),
    "addon-syrup": ("Flavor Syrup", 10),
    "addon-oat": ("Oat Milk", 15),
    "addon-cream": ("Whipped Cream", 10),
}

# In-memory cart: list of dicts, each with a unique row id for removal.
cart = []
_next_row_id = 1
_scroll_animation_proxy = None
_scroll_animation_frame = None
_scroll_original_behavior = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def peso(amount):
    return f"₱{amount:,.2f}"


def get_current_selection():
    """Read the order form's current state and compute the live unit price."""
    drink_select = document.getElementById("drink-select")
    drink_key = drink_select.value
    drink_name, base_price = DRINK_PRICES[drink_key]

    size_inputs = document.getElementsByName("size")
    size_value = "regular"
    for i in range(size_inputs.length):
        el = size_inputs.item(i)
        if el.checked:
            size_value = el.value
            break

    chosen_addons = []
    for addon_id, (label, price) in ADDON_PRICES.items():
        el = document.getElementById(addon_id)
        if el.checked:
            chosen_addons.append((addon_id, label, price))

    qty_input = document.getElementById("qty-input")
    try:
        qty = max(1, int(qty_input.value or 1))
    except ValueError:
        qty = 1

    unit_price = base_price + SIZE_SURCHARGE[size_value] + sum(p for _, _, p in chosen_addons)
    line_total = unit_price * qty

    return {
        "drink_key": drink_key,
        "drink_name": drink_name,
        "size": size_value,
        "addons": chosen_addons,
        "qty": qty,
        "unit_price": unit_price,
        "line_total": line_total,
    }


def render_order_table():
    """Rebuild the order table and grand total from the current cart state."""
    body = document.getElementById("order-table-body")
    body.innerHTML = ""

    if not cart:
        row = document.createElement("tr")
        row.innerHTML = '<td colspan="4" class="empty-msg">No items yet — add a drink to get started.</td>'
        body.appendChild(row)
    else:
        for item in cart:
            row = document.createElement("tr")

            addon_text = ""
            if item["addons"]:
                addon_text = "<br><span class='muted'>+ " + ", ".join(a[1] for a in item["addons"]) + "</span>"
            size_label = "Large" if item["size"] == "large" else "Regular"

            name_cell = document.createElement("td")
            name_cell.innerHTML = f"{item['drink_name']} <span class='muted'>({size_label})</span>{addon_text}"

            qty_cell = document.createElement("td")
            qty_cell.textContent = str(item["qty"])

            price_cell = document.createElement("td")
            price_cell.textContent = peso(item["line_total"])

            action_cell = document.createElement("td")
            remove_btn = document.createElement("button")
            remove_btn.className = "remove-btn"
            remove_btn.textContent = "Remove"
            remove_btn.type = "button"

            # Dynamically created element: bind its click handler manually
            # via create_proxy, since it did not exist when the page first loaded.
            row_id = item["id"]
            proxy = create_proxy(lambda evt, rid=row_id: remove_item_by_id(rid))
            remove_btn.addEventListener("click", proxy)

            action_cell.appendChild(remove_btn)

            row.appendChild(name_cell)
            row.appendChild(qty_cell)
            row.appendChild(price_cell)
            row.appendChild(action_cell)
            body.appendChild(row)

    grand_total = sum(item["line_total"] for item in cart)
    document.getElementById("grand-total").textContent = peso(grand_total)


def remove_item_by_id(row_id):
    global cart
    cart = [item for item in cart if item["id"] != row_id]
    render_order_table()
    confirmation = document.getElementById("order-confirmation")
    confirmation.classList.add("hidden")


# ---------------------------------------------------------------------------
# Event handlers — Order builder
# ---------------------------------------------------------------------------

def update_preview(event=None):
    """change/input handler: recompute the live line-price preview."""
    selection = get_current_selection()
    document.getElementById("preview-price").textContent = peso(selection["line_total"])


def add_to_order(event):
    """click handler: add the current selection to the order as a new row."""
    global _next_row_id
    selection = get_current_selection()
    selection["id"] = _next_row_id
    _next_row_id += 1
    cart.append(selection)
    render_order_table()

    # Reset quantity back to 1 after adding, and refresh the preview.
    document.getElementById("qty-input").value = "1"
    update_preview()

    confirmation = document.getElementById("order-confirmation")
    confirmation.classList.add("hidden")


def place_order(event):
    """click handler: 'checkout' the current cart with a generated order code."""
    confirmation = document.getElementById("order-confirmation")

    if not cart:
        confirmation.innerHTML = "Your order is empty — add at least one drink first."
        confirmation.classList.remove("hidden")
        return

    grand_total = sum(item["line_total"] for item in cart)
    now = datetime.now()
    order_code = f"KK-{now.strftime('%H%M%S')}"

    confirmation.innerHTML = (
        f"<strong>Order placed!</strong> Code <strong>{order_code}</strong> &middot; "
        f"Total {peso(grand_total)}. Please pay at the cart window and show this code."
    )
    confirmation.classList.remove("hidden")

    cart.clear()
    render_order_table()


# ---------------------------------------------------------------------------
# Event handler — Loyalty rewards
# ---------------------------------------------------------------------------

def calc_loyalty(event):
    """click handler: compute free cups under the 'buy 9 get 1 free' program."""
    loyalty_input = document.getElementById("loyalty-input")
    result = document.getElementById("loyalty-result")
    summary = document.getElementById("loyalty-summary")
    free_counter = document.getElementById("loyalty-free")
    next_reward = document.getElementById("loyalty-next")
    progress_label = document.getElementById("loyalty-progress-label")
    progress_bar = document.getElementById("loyalty-progress-bar")

    try:
        cups = int(loyalty_input.value or 0)
    except ValueError:
        cups = 0

    if cups < 0:
        result.textContent = "Please enter a positive number of cups."
        summary.classList.add("hidden")
        return

    free_cups = cups // 9
    remainder = cups % 9
    cups_to_next_free = 9 if cups == 0 else (9 - remainder) % 9
    if cups > 0 and remainder == 0:
        cups_to_next_free = 0

    progress_pct = 0 if cups == 0 else min(100, (remainder / 9) * 100)
    if cups > 0 and remainder == 0:
        progress_pct = 100

    if free_cups == 0:
        result.textContent = f"Buy {cups_to_next_free or 9} more cup(s) to earn your first free coffee!"
    else:
        msg = f"You've earned {free_cups} free cup(s) so far!"
        if cups_to_next_free:
            msg += f" {cups_to_next_free} more cup(s) until your next one."
        result.textContent = msg

    summary.classList.remove("hidden")
    free_counter.textContent = str(free_cups)

    if cups_to_next_free == 0:
        next_reward.textContent = "Unlocked"
        progress_label.textContent = "100%"
    else:
        next_reward.textContent = f"{cups_to_next_free} cups"
        progress_label.textContent = f"{round(progress_pct)}%"

    progress_bar.style.width = f"{max(8, progress_pct)}%" if cups > 0 else "0%"
    progress_bar.style.background = "linear-gradient(90deg, #D9A441, #C08A2A)"


# ---------------------------------------------------------------------------
# Event handlers — Feedback form
# ---------------------------------------------------------------------------

def update_char_count(event):
    """input handler: live character counter for the feedback message box."""
    message_box = document.getElementById("feedback-message")
    count = len(message_box.value)
    document.getElementById("char-count").textContent = f"{count} / 200 characters"


def handle_feedback_submit(event):
    """submit handler: validate, render a new feedback card, reset the form."""
    event.preventDefault()  # stop the browser's default full-page form submit

    name_input = document.getElementById("feedback-name")
    rating_select = document.getElementById("feedback-rating")
    message_box = document.getElementById("feedback-message")

    name = name_input.value.strip()
    message = message_box.value.strip()
    rating = int(rating_select.value)

    if not name or not message:
        return  # the "required" attributes normally catch this; guard anyway

    card = document.createElement("div")
    card.className = "feedback-card"

    stars = "★" * rating + "☆" * (5 - rating)
    today = datetime.now().strftime("%b %d, %Y")

    card.innerHTML = (
        f"<div class='feedback-card-head'><strong>{name}</strong>"
        f"<span class='stars'>{stars}</span></div>"
        f"<p>{message}</p>"
        f"<span class='feedback-date'>{today}</span>"
    )

    feedback_list = document.getElementById("feedback-list")
    feedback_list.insertBefore(card, feedback_list.firstChild)

    # Reset the form for the next entry.
    name_input.value = ""
    message_box.value = ""
    rating_select.value = "5"
    document.getElementById("char-count").textContent = "0 / 200 characters"


# ---------------------------------------------------------------------------
# Event handler — Mobile navigation
# ---------------------------------------------------------------------------

def toggle_nav(event):
    """click handler: open/close the mobile navigation menu."""
    nav = document.getElementById("nav-links")
    nav.classList.toggle("open")
    document.getElementById("nav-toggle").setAttribute(
        "aria-expanded", str(nav.classList.contains("open")).lower()
    )


def navigate_to_section(event):
    """Smooth-scroll to a header destination and close the mobile menu."""
    global _scroll_animation_proxy, _scroll_animation_frame, _scroll_original_behavior

    event.preventDefault()
    link = event.currentTarget
    href = link.getAttribute("href")
    target = document.getElementById(href[1:])

    window.history.pushState(None, "", href)

    if _scroll_animation_frame is not None:
        window.cancelAnimationFrame(_scroll_animation_frame)
        _scroll_animation_proxy.destroy()
        document.documentElement.style.scrollBehavior = _scroll_original_behavior
        _scroll_animation_proxy = None
        _scroll_animation_frame = None
        _scroll_original_behavior = None

    start_y = window.scrollY
    header_height = document.querySelector(".site-header").getBoundingClientRect().height
    target_y = start_y + target.getBoundingClientRect().top - header_height
    max_y = document.documentElement.scrollHeight - window.innerHeight
    target_y = max(0, min(target_y, max_y))

    if abs(target_y - start_y) > 1:
        _scroll_original_behavior = document.documentElement.style.scrollBehavior
        document.documentElement.style.scrollBehavior = "auto"
        started_at = window.performance.now()
        duration = 650

        def animate_scroll(timestamp):
            global _scroll_animation_proxy, _scroll_animation_frame, _scroll_original_behavior

            progress = min((float(timestamp) - started_at) / duration, 1)
            eased_progress = 1 - (1 - progress) ** 3
            position = start_y + (target_y - start_y) * eased_progress
            window.scrollTo(0, position)

            if progress < 1:
                _scroll_animation_frame = window.requestAnimationFrame(_scroll_animation_proxy)
            else:
                document.documentElement.style.scrollBehavior = _scroll_original_behavior
                _scroll_animation_proxy.destroy()
                _scroll_animation_proxy = None
                _scroll_animation_frame = None
                _scroll_original_behavior = None

        _scroll_animation_proxy = create_proxy(animate_scroll)
        _scroll_animation_frame = window.requestAnimationFrame(_scroll_animation_proxy)

    nav = document.getElementById("nav-links")
    nav.classList.remove("open")
    document.getElementById("nav-toggle").setAttribute("aria-expanded", "false")


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

render_order_table()
update_preview()

# Reveal the page once PyScript has finished initializing.
document.body.classList.add("py-ready")
