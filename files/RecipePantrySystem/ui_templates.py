"""All HTML pages of the Recipe Pantry System, kept inside Python.

They are Jinja2 templates stored as strings; app.py loads them with a DictLoader,
so there are no .html files in the project. Page names are the dictionary keys.
"""

TEMPLATES = {
    "_back.html": r"""<div class="back-row">
  <a class="btn back-btn" href="{{ url_for('dashboard') }}"><i class="fas fa-arrow-left"></i> Back to dashboard</a>
</div>
""",

    "_ideas.html": r"""{# "What can I cook?" -- dish ideas from the pantry. Needs `ideas` from suggestions.build_dish_ideas #}
{% macro dish(d, pick=false) %}
<article class="dish {{ 'ready' if d.ready else 'almost' }}{{ ' pick' if pick }}">
  <div class="dish-head">
    <strong>{{ d.name }}</strong>
    {% if d.ready %}<span class="pill ok">Ready</span>
    {% else %}<span class="pill short">Missing {{ d.missing | length }}</span>{% endif %}
  </div>
  <div class="muted small">For {{ d.servings }} serving{{ 's' if d.servings != 1 else '' }} &middot; you have {{ d.covered }} of {{ d.total }} ingredients</div>
  <div class="meter" role="img" aria-label="{{ d.percent }}% of the ingredients covered"><span style="width: {{ d.percent }}%"></span></div>
  {% if pick %}
    <p class="dish-reason"><i class="fas fa-wand-magic-sparkles"></i> {{ d.reason }}</p>
  {% elif d.expiry_note %}
    <p class="dish-reason soft"><i class="fas fa-hourglass-half"></i> {{ d.expiry_note }}</p>
  {% endif %}
  {% if d.missing %}
  <div class="chips">
    <span class="chips-label">Missing</span>
    {% for m in d.missing %}<span class="chip">{{ m.name }} <em>{{ m.shortage }}{% if m.unit %} {{ m.unit }}{% endif %}</em></span>{% endfor %}
  </div>
  {% endif %}
  <a class="btn small {{ '' if d.ready else 'secondary' }}" href="{{ url_for('check.result', r=d.key) }}">Check this recipe</a>
</article>
{% endmacro %}

<section class="ideas">
  <h2 class="ideas-title"><span class="title-ico sm"><i class="fas fa-lightbulb"></i></span>What can I cook?</h2>

  {% if ideas.recipe_count == 0 %}
    <div class="card">
      <p class="muted">Save a few recipes and dishes that fit what is in your pantry will show up here.</p>
      <a class="btn" href="{{ url_for('recipes.new_recipe') }}">Add a recipe</a>
    </div>

  {% elif ideas.pantry_count == 0 %}
    <div class="card">
      <p class="muted">Add some ingredients to your pantry and this will show which of your {{ ideas.recipe_count }} saved recipe{{ 's' if ideas.recipe_count != 1 else '' }} you can make.</p>
    </div>

  {% elif not ideas.any_close %}
    <div class="card">
      <p class="muted">None of your {{ ideas.recipe_count }} saved recipe{{ 's' if ideas.recipe_count != 1 else '' }} {{ 'is' if ideas.recipe_count == 1 else 'are' }} within a few ingredients of your pantry yet. Add more ingredients and ideas will appear.</p>
    </div>

  {% else %}
    {% if ideas.picks %}
    <div class="idea-block picks-block">
      <h3><i class="fas fa-star"></i> Suggested for you</h3>
      <p class="muted small">Top picks from your {{ ideas.recipe_count }} saved recipes, ranked by how complete they are and what is about to expire.</p>
      <div class="dish-grid">{% for d in ideas.picks %}{{ dish(d, true) }}{% endfor %}</div>
    </div>
    {% endif %}

    {% if ideas.ready %}
    <div class="idea-block">
      <h3><i class="fas fa-circle-check"></i> Ready to cook</h3>
      <p class="muted small">You have everything for {{ 'these' if ideas.ready | length > 1 else 'this' }}.</p>
      <div class="dish-grid">{% for d in ideas.ready %}{{ dish(d) }}{% endfor %}</div>
    </div>
    {% endif %}

    {% if ideas.almost %}
    <div class="idea-block">
      <h3><i class="fas fa-basket-shopping"></i> Almost there</h3>
      <p class="muted small">Only a few ingredients short.</p>
      <div class="dish-grid">{% for d in ideas.almost %}{{ dish(d) }}{% endfor %}</div>
      {% if ideas.almost_hidden %}<p class="muted small">+ {{ ideas.almost_hidden }} more that need a few more ingredients.</p>{% endif %}
    </div>
    {% endif %}
  {% endif %}
</section>
""",

    "base.html": r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{% block title %}Recipe Pantry System{% endblock %}</title>
<link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Playfair+Display:wght@400;700;900&family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{{ url_for('stylesheet', v=css_version) }}">
</head>
<body>
{% set ep = request.endpoint or '' %}
{% if logged_in_nav %}
<header class="topbar">
  <a class="brand" href="{{ url_for('dashboard') }}">
    <span class="brand-ico"><i class="fas fa-utensils"></i></span>
    <span class="brand-name">Recipe <span>Pantry</span> System<small class="brand-sub">Cook with what you have</small></span>
  </a>
  <nav>
    <a href="{{ url_for('dashboard') }}" class="n-dash {{ 'current' if ep == 'dashboard' }}"><i class="fas fa-gauge-high"></i><span>Dashboard</span></a>
    <a href="{{ url_for('pantry.list_view') }}" class="n-pantry {{ 'current' if ep.startswith('pantry') }}"><i class="fas fa-boxes-stacked"></i><span>Pantry</span></a>
    <a href="{{ url_for('recipes.list_view') }}" class="n-recipes {{ 'current' if ep.startswith('recipes') }}"><i class="fas fa-book-open"></i><span>Recipes</span></a>
    <a href="{{ url_for('check.select_recipe') }}" class="n-check {{ 'current' if ep.startswith('check') }}"><i class="fas fa-clipboard-check"></i><span>Check a recipe</span></a>
    <form action="{{ url_for('auth.logout') }}" method="post" style="display:inline">
      <button class="btn ghost logout-btn" type="submit"><i class="fas fa-right-from-bracket"></i> Log out</button>
    </form>
  </nav>
</header>
{% endif %}
<main>
<div class="wrap {% block wrapclass %}{% endblock %}">
  {% with messages = get_flashed_messages(with_categories=true) %}
    {% for category, message in messages %}
      <div class="flash {{ category }}">{{ message }}</div>
    {% endfor %}
  {% endwith %}
  {% block content %}{% endblock %}
</div>
</main>
<footer><strong>Recipe <span>Pantry</span> System</strong><br>Know what you have. Buy only what you need.</footer>
<script>

document.addEventListener('click', function (e) {
  var a = e.target.closest('a');
  if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
  if (a.target || a.hasAttribute('download') || a.hasAttribute('onclick')) return;
  var url = new URL(a.href, location.href);
  if (url.origin !== location.origin || (url.pathname === location.pathname && url.search === location.search)) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  e.preventDefault();
  document.body.classList.add('leaving');
  setTimeout(function () { location.href = a.href; }, 220);
});

window.addEventListener('pageshow', function (e) { if (e.persisted) document.body.classList.remove('leaving'); });
</script>
</body>
</html>
""",

    "check_cooked.html": r"""{% extends "base.html" %}
{% block content %}
<h1>Pantry updated</h1>
<p class="sub">{% if cooked and cooked | length > 1 %}Cooked {{ cooked | join(', ') }}. {% endif %}These amounts were subtracted from your pantry.</p>
<div class="card">
  <table>
    <tr><th>Ingredient</th><th>Before</th><th>After</th></tr>
    {% for c in changes %}
    <tr><td>{{ c.name }}</td><td class="muted">{{ c.before }} {{ c.unit }}</td><td><strong>{{ c.after }} {{ c.unit }}</strong></td></tr>
    {% endfor %}
  </table>
</div>
{% if low %}
<div class="flash error">
  <strong>Running low:</strong>
  {% for l in low %}{{ l.name }} ({{ l.quantity }} {{ l.unit }} left){% if not loop.last %}, {% endif %}{% endfor %}
</div>
{% endif %}
<div class="row">
  <a class="btn back-btn" href="{{ url_for('dashboard') }}"><i class="fas fa-arrow-left"></i> Back to dashboard</a>
  <a class="btn secondary" href="{{ url_for('check.select_recipe') }}">Check another recipe</a>
</div>
{% endblock %}
""",

    "check_result.html": r"""{% extends "base.html" %}
{% block content %}
<div class="row" style="justify-content:space-between">
  <h1>
    {% if group %}{{ group.row.group_name }}
    {% elif multi %}Checking {{ sections | length }} recipes
    {% else %}{{ sections[0].recipe.recipe_name }}{% endif %}
  </h1>
  <div class="row">
    <a class="btn ghost" href="{{ request.script_root }}{{ request.path }}" onclick="location.reload(); return false;"><i class="fas fa-rotate"></i> Refresh</a>
    <a class="btn ghost" href="{{ url_for('check.select_recipe') }}">{{ 'Choose other recipes' if multi else 'Choose another recipe' }}</a>
  </div>
</div>
{% if multi %}
<p class="sub">{% for s in sections %}{{ s.recipe.recipe_name }} &times;{{ s.servings }}{% if not loop.last %} &middot; {% endif %}{% endfor %}</p>
{% else %}
<p class="sub">For {{ sections[0].servings }} serving{{ 's' if sections[0].servings != 1 else '' }}</p>
{% endif %}

{% if report.all_enough %}
<div class="flash ok">
  {% if multi %}You have enough ingredients for all {{ sections | length }} recipes together.
  {% else %}You have enough ingredients for this recipe.{% endif %}
</div>
{% else %}
<div class="flash error">
  You are missing {{ report.missing | length }} of {{ report.rows | length }} ingredients{% if multi %} across all the recipes together{% endif %}.
</div>
{% endif %}

{% if multi and report.only_together %}
<div class="flash warn">
  <strong>Shared ingredients:</strong> each recipe is fine on its own for
  {% for r in report.only_together %}<strong>{{ r.ingredient_name }}</strong>{{ ', ' if not loop.last }}{% endfor %},
  but together they need more than you have.
</div>
{% endif %}

{% if multi %}
  <div class="section-split"><span><i class="fas fa-list-check"></i> Recipe by recipe</span></div>
  <p class="muted small note">Each recipe is checked on its own against everything in your pantry.</p>

  {% for s in sections %}
  <div class="card recipe-card">
    <div class="rc-head">
      <span class="rc-num">{{ loop.index }}</span>
      <div class="rc-title">
        <strong>{{ s.recipe.recipe_name }}</strong>
        <span class="muted small">{{ s.servings }} serving{{ 's' if s.servings != 1 else '' }}</span>
      </div>
      {% if s.report.all_enough %}<span class="pill ok">Ready</span>
      {% else %}<span class="pill short">Missing {{ s.report.missing | length }}</span>{% endif %}
    </div>
    <table>
      <tr><th>Ingredient</th><th>Need</th><th>Have</th><th></th></tr>
      {% for i in s.report.rows %}
      <tr>
        <td>{{ i.ingredient_name }}</td>
        <td>{{ i.quantity_needed }} {{ i.unit }}</td>
        <td>{{ i.have }} {{ i.unit }}</td>
        <td>
          {% if i.status == 'enough' %}<span class="pill ok">Enough</span>
          {% else %}<span class="pill short">Short by {{ i.shortage }} {{ i.unit }}</span>{% endif %}
        </td>
      </tr>
      {% endfor %}
    </table>
  </div>
  {% endfor %}

  <div class="section-split together"><span><i class="fas fa-layer-group"></i> Everything together</span></div>
  <p class="muted small note">The recipes share your pantry, so any ingredient used by more than one is added up first.</p>

  <div class="card together-card">
    <table>
      <tr><th>Ingredient</th><th>Total need</th><th>Have</th><th>Needed by</th><th></th></tr>
      {% for i in report.rows %}
      <tr>
        <td>{{ i.ingredient_name }}</td>
        <td>{{ i.quantity_needed }} {{ i.unit }}</td>
        <td>{{ i.have }} {{ i.unit }}</td>
        <td class="muted small">
          {% for u in i.used_by %}{{ u.recipe }} {{ u.quantity }}{% if i.unit %} {{ i.unit }}{% endif %}{% if not loop.last %}<br>{% endif %}{% endfor %}
        </td>
        <td>
          {% if i.status == 'enough' %}<span class="pill ok">Enough</span>
          {% else %}<span class="pill short">Short by {{ i.shortage }} {{ i.unit }}</span>
            {% if i.only_together %}<div class="muted small tight">only short when combined</div>{% endif %}{% endif %}
        </td>
      </tr>
      {% endfor %}
    </table>
  </div>
{% else %}
  <div class="card">
    <table>
      <tr><th>Ingredient</th><th>Need</th><th>Have</th><th></th></tr>
      {% for i in report.rows %}
      <tr>
        <td>{{ i.ingredient_name }}</td>
        <td>{{ i.quantity_needed }} {{ i.unit }}</td>
        <td>{{ i.have }} {{ i.unit }}</td>
        <td>
          {% if i.status == 'enough' %}<span class="pill ok">Enough</span>
          {% else %}<span class="pill short">Short by {{ i.shortage }} {{ i.unit }}</span>{% endif %}
        </td>
      </tr>
      {% endfor %}
    </table>
  </div>
{% endif %}

{% if report.all_enough %}
<div class="card">
  <strong>{{ 'Cook everything now?' if multi else 'Cook this recipe now?' }}</strong>
  <p class="muted">
    {% if multi %}Cooking subtracts the combined amounts for all {{ sections | length }} recipes from your pantry.
    {% else %}Cooking subtracts these amounts from your pantry.{% endif %}
  </p>
  <form method="post" action="{{ url_for('check.cook') }}">
    {% if group %}<input type="hidden" name="group" value="{{ group.row.group_id }}">
    {% else %}{% for p in pairs %}<input type="hidden" name="r" value="{{ p }}">{% endfor %}{% endif %}
    <div class="row">
      <button class="btn" type="submit">{{ 'Yes, cook everything' if multi else 'Yes, cook now' }}</button>
      <a class="btn ghost" href="{{ url_for('dashboard') }}">Not now</a>
    </div>
  </form>
</div>
{% else %}
<form method="post" action="{{ url_for('check.to_shopping_list') }}">
  {% if group %}<input type="hidden" name="group" value="{{ group.row.group_id }}">
  {% else %}{% for p in pairs %}<input type="hidden" name="r" value="{{ p }}">{% endfor %}{% endif %}
  <button class="btn" type="submit">See shopping list</button>
</form>
{% endif %}
{% include '_back.html' %}
{% endblock %}
""",

    "check_select.html": r"""{% extends "base.html" %}
{% block content %}
<div class="row" style="justify-content:space-between">
  <h1><span class="title-ico"><i class="fas fa-clipboard-check"></i></span>Check recipes</h1>
  <a class="btn ghost" href="{{ request.script_root }}{{ request.path }}" onclick="location.reload(); return false;"><i class="fas fa-rotate"></i> Refresh</a>
</div>
<p class="sub">Tick one recipe, or several to check a whole feast at once. Each recipe gets its own servings.</p>

{% if not recipes %}
<div class="card">
  <p class="muted">No recipes found.</p>
  <a class="btn" href="{{ url_for('recipes.new_recipe') }}">Create a recipe</a>
</div>
{% else %}

{% if groups %}
<div class="card">
  <h2 class="card-title"><i class="fas fa-layer-group"></i> Saved groups</h2>
  <p class="muted small">A group is a saved set of recipes that you check together, like a feast.</p>
  {% for g in groups %}
  <div class="group-row">
    <div class="group-info">
      <strong>{{ g.row.group_name }}</strong>
      <span class="muted small">
        {% if g.members %}{% for m in g.members %}{{ m.recipe_name }} &times;{{ m.servings }}{% if not loop.last %} &middot; {% endif %}{% endfor %}
        {% else %}No recipes left in this group.{% endif %}
      </span>
    </div>
    <div class="row">
      {% if g.members %}<a class="btn small" href="{{ url_for('check.result', group=g.row.group_id) }}"><i class="fas fa-clipboard-check"></i> Check group</a>{% endif %}
      <a class="btn ghost small" href="{{ url_for('check.select_recipe', group=g.row.group_id) }}"><i class="fas fa-pen"></i> Edit</a>
      <form action="{{ url_for('groups.delete', group_id=g.row.group_id) }}" method="post" onsubmit="return confirm('Delete this group? Your recipes are not deleted.');">
        <button class="btn danger small" type="submit"><i class="fas fa-trash"></i></button>
      </form>
    </div>
  </div>
  {% endfor %}
</div>
{% endif %}

<div class="card">
  <form method="post" id="pick-form" action="{{ url_for('check.select_recipe') }}">
    <div class="row" style="justify-content:space-between; margin-bottom:10px">
      <span class="pick-heading">Recipes <span class="pill ok" id="pick-count">0 selected</span></span>
      <div class="row">
        <button type="button" class="btn ghost small" id="pick-all">Select all</button>
        <button type="button" class="btn ghost small" id="pick-none">Clear</button>
      </div>
    </div>

    <div class="pick-list">
      {% for r in recipes %}
      {% set pf = prefill[r.row.recipe_id] %}
      <label class="pick-row {{ 'on' if pf.picked }}">
        <input type="checkbox" name="pick" value="{{ r.row.recipe_id }}" {{ 'checked' if pf.picked }}>
        <span class="pick-name"><strong>{{ r.row.recipe_name }}</strong><span class="muted small">makes {{ r.row.servings }}</span></span>
        <span class="pick-serv">
          <span class="muted small">cook</span>
          <input type="number" min="1" name="servings_{{ r.row.recipe_id }}" value="{{ pf.servings }}" aria-label="Servings of {{ r.row.recipe_name }}">
          <span class="muted small">servings</span>
        </span>
      </label>
      {% endfor %}
    </div>

    <button class="btn" type="submit"><i class="fas fa-clipboard-check"></i> Check my pantry</button>

    <div class="group-save">
      <h3><i class="fas fa-layer-group"></i> Planning a feast?</h3>
      <p class="muted small">Tick two or more recipes, name the group, and save it. Next time you can check the whole group in one click.</p>
      <div class="row nowrap">
        <input type="text" name="group_name" id="group-name" maxlength="60" placeholder="e.g. Christmas feast" value="{{ group_name }}">
        <button type="submit" class="btn secondary" id="group-save-btn" formaction="{{ url_for('groups.save') }}"><i class="fas fa-floppy-disk"></i> Save as group</button>
      </div>
    </div>
  </form>
</div>
{% endif %}
{% include '_back.html' %}

<script>
(function () {
  var form = document.getElementById('pick-form');
  if (!form) return;
  var boxes = [].slice.call(form.querySelectorAll('input[name=pick]'));
  var count = document.getElementById('pick-count');

  function sync() {
    var n = 0;
    boxes.forEach(function (b) {
      b.closest('.pick-row').classList.toggle('on', b.checked);
      if (b.checked) n++;
    });
    count.textContent = n + ' selected';
  }
  boxes.forEach(function (b) { b.addEventListener('change', sync); });

  
  [].forEach.call(form.querySelectorAll('.pick-serv input'), function (inp) {
    inp.addEventListener('input', function () {
      var b = inp.closest('.pick-row').querySelector('input[name=pick]');
      if (!b.checked) { b.checked = true; sync(); }
    });
  });

  document.getElementById('pick-all').addEventListener('click', function () {
    boxes.forEach(function (b) { b.checked = true; }); sync();
  });
  document.getElementById('pick-none').addEventListener('click', function () {
    boxes.forEach(function (b) { b.checked = false; }); sync();
  });

  
  document.getElementById('group-name').addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { e.preventDefault(); document.getElementById('group-save-btn').click(); }
  });
  sync();
})();
</script>
{% endblock %}
""",

    "dashboard.html": r"""{% extends "base.html" %}
{% block content %}
<h1>Hello, {{ user.name.split(' ')[0] }}</h1>
<p class="sub">What would you like to do?</p>
<div class="menu">
  <a class="m-check" href="{{ url_for('check.select_recipe') }}"><i class="fas fa-clipboard-check m-ico"></i><strong>Check a recipe</strong><span>See what you have and what you still need to buy.</span><em class="go"><i class="fas fa-arrow-right"></i></em></a>
  <a class="m-pantry" href="{{ url_for('pantry.list_view') }}"><i class="fas fa-boxes-stacked m-ico"></i><strong>Manage pantry</strong><span>{{ pantry_count }} ingredient{{ 's' if pantry_count != 1 else '' }} on hand.</span><em class="go"><i class="fas fa-arrow-right"></i></em></a>
  <a class="m-recipes" href="{{ url_for('recipes.list_view') }}"><i class="fas fa-book-open m-ico"></i><strong>Manage recipes</strong><span>{{ recipe_count }} saved recipe{{ 's' if recipe_count != 1 else '' }}.</span><em class="go"><i class="fas fa-arrow-right"></i></em></a>
</div>
<form action="{{ url_for('auth.logout') }}" method="post" style="margin-top:18px">
  <button class="btn ghost logout-btn" type="submit"><i class="fas fa-right-from-bracket"></i> Log out</button>
</form>
{% endblock %}
""",

    "forgot_password.html": r"""{% extends "base.html" %}
{% block wrapclass %}narrow{% endblock %}
{% block content %}
<div class="card">
{% if step == 1 %}
  <h1>Reset your password</h1>
  <p class="sub">Enter the email you signed up with.</p>
  <form method="post">
    <div class="field"><label for="email">Email</label>
      <input id="email" name="email" type="email" value="{{ values.email or '' }}"></div>
    <button class="btn" type="submit">Send reset code</button>
  </form>
{% else %}
  <h1>Enter your reset code</h1>
  <p class="sub">Demo code: <strong>{{ demo_code }}</strong>.</p>
  <form method="post" action="{{ url_for('auth.forgot_password_reset') }}">
    <div class="field"><label for="code">Reset code</label>
      <input id="code" name="code" type="text" maxlength="6"></div>
    <div class="field"><label for="password">New password</label>
      <input id="password" name="password" type="password"></div>
    <button class="btn" type="submit">Save new password</button>
  </form>
{% endif %}
  <p style="margin-top:14px"><a href="{{ url_for('auth.login') }}" class="muted">Back to log in</a></p>
</div>
{% endblock %}
""",

    "landing.html": r"""{% extends "base.html" %}
{% block title %}Recipe Pantry System{% endblock %}
{% block wrapclass %}narrow{% endblock %}
{% block content %}
<div class="card hero">
  <span class="slbl">Welcome to your kitchen</span>
  <h1>Recipe Pantry System</h1>
  <p class="sub">Check whether you have enough ingredients for a recipe, and manage what -- and how much -- you still need.</p>
  <div class="row">
    <a class="btn" href="{{ url_for('auth.login') }}">Log in</a>
    <a class="btn secondary" href="{{ url_for('auth.signup') }}">Sign up</a>
  </div>
</div>
{% endblock %}
""",

    "login.html": r"""{% extends "base.html" %}
{% block wrapclass %}narrow{% endblock %}
{% block content %}
<div class="card">
  <h1>Log in</h1>
  <p class="sub">Welcome back.</p>
  <form method="post">
    <div class="field"><label for="email">Email</label>
      <input id="email" name="email" type="email" value="{{ values.email or '' }}"></div>
    <div class="field"><label for="password">Password</label>
      <input id="password" name="password" type="password"></div>
    <button class="btn" type="submit">Log in</button>
  </form>
  <p style="margin-top:14px">
    <a href="{{ url_for('auth.forgot_password') }}">Forgot your password?</a> &middot;
    <a href="{{ url_for('auth.signup') }}">Create an account</a>
  </p>
</div>
{% endblock %}
""",

    "pantry.html": r"""{% extends "base.html" %}
{% block content %}
<div class="row" style="justify-content:space-between">
  <h1><span class="title-ico"><i class="fas fa-boxes-stacked"></i></span>Pantry</h1>
  <div class="row">
    <a class="btn ghost" href="{{ request.script_root }}{{ request.path }}" onclick="location.reload(); return false;"><i class="fas fa-rotate"></i> Refresh</a>
    <a class="btn" href="{{ url_for('pantry.new_item') }}">Add ingredient</a>
  </div>
</div>
<p class="sub">The ingredients you have at home.</p>
<div class="card">
  {% if not items %}
    <p class="muted">Your pantry is empty. Add your first ingredient to get started.</p>
  {% else %}
    <table>
      <tr><th>Ingredient</th><th>Quantity</th><th>Expiry</th><th></th></tr>
      {% for it in items %}
      <tr>
        <td>{{ it.ingredient_name }}</td>
        <td>{{ it.quantity_on_hand }} {{ it.unit }}</td>
        <td class="muted">{{ it.expiry_date or '--' }}</td>
        <td>
          <form action="{{ url_for('pantry.delete', pantry_item_id=it.pantry_item_id) }}" method="post" style="display:inline">
            <button class="btn danger" type="submit" style="padding:4px 10px">Delete</button>
          </form>
        </td>
      </tr>
      {% endfor %}
    </table>
  {% endif %}
</div>

{% include '_ideas.html' %}

{% include '_back.html' %}
{% endblock %}
""",

    "pantry_form.html": r"""{% extends "base.html" %}
{% block wrapclass %}narrow{% endblock %}
{% block content %}
<h1>Add or update an ingredient</h1>
<p class="sub">If this ingredient is already in your pantry, its quantity is updated instead of added as a duplicate.</p>
<div class="card">
  <form method="post">
    <div class="field"><label for="name">Ingredient name</label>
      <input id="name" name="name" type="text" value="{{ values.name or '' }}"></div>
    <div class="row">
      <div class="field" style="flex:2"><label for="quantity">Quantity</label>
        <input id="quantity" name="quantity" type="text" inputmode="decimal" value="{{ values.quantity or '' }}"></div>
      <div class="field" style="flex:1"><label for="unit">Unit (optional)</label>
        <input id="unit" name="unit" type="text" placeholder="g, ml, pcs... or leave blank" value="{{ values.unit or '' }}"></div>
    </div>
    <div class="field"><label for="expiry_date">Expiry date (optional)</label>
      <input id="expiry_date" name="expiry_date" type="date" value="{{ values.expiry_date or '' }}"></div>
    <button class="btn" type="submit">Save ingredient</button>
    <a class="btn ghost" href="{{ url_for('pantry.list_view') }}">Cancel</a>
  </form>
</div>
{% endblock %}
""",

    "recipe_form.html": r"""{% extends "base.html" %}
{% set volume_units = ['ml', 'l', 'tsp', 'tbsp', 'fl oz', 'cup', 'pt', 'qt', 'gal'] %}
{% set weight_units = ['mg', 'g', 'kg', 'oz', 'lb'] %}
{% macro ing_row(name='', qty='', unit='') %}
<div class="ing-row">
  <input type="text" name="ingredient_name" placeholder="Ingredient" value="{{ name }}">
  <input type="number" name="ingredient_quantity" class="qty-input" placeholder="Qty" min="0" step="any" value="{{ qty }}" aria-label="Quantity">
  <div class="unit-group">
    <input type="number" class="unit-num" placeholder="e.g. 12" min="0" step="any" aria-label="Amount per unit (optional)">
    <select class="unit-select" aria-label="Unit">
      <option value="">Unit</option>
      <optgroup label="Volume">
        {% for v in volume_units %}<option value="{{ v }}">{{ v }}</option>
        {% endfor %}
      </optgroup>
      <optgroup label="Weight (Mass)">
        {% for v in weight_units %}<option value="{{ v }}">{{ v }}</option>
        {% endfor %}
      </optgroup>
    </select>
    <input type="hidden" name="ingredient_unit" class="unit-value" value="{{ unit }}">
  </div>
  <button type="button" class="btn ghost" onclick="removeRow(this)" aria-label="Remove ingredient">&times;</button>
</div>
{% endmacro %}
{% block content %}
<h1>{{ 'Edit recipe' if recipe_id else 'New recipe' }}</h1>
<p class="sub">Add the recipe name, how many servings it makes, and each ingredient.</p>
<div class="card">
  <form method="post">
    <div class="row">
      <div class="field" style="flex:2"><label for="recipe_name">Recipe name</label>
        <input id="recipe_name" name="recipe_name" type="text" value="{{ values.recipe_name or '' }}"></div>
      <div class="field" style="flex:1"><label for="servings">Servings</label>
        <input id="servings" name="servings" type="text" inputmode="numeric" value="{{ values.servings or '' }}"></div>
    </div>

    <label>Ingredients <span class="muted" style="font-weight:400">&middot; unit is optional</span></label>
    <div id="rows">
      {% for name, qty, unit in values.rows %}
      {{ ing_row(name, qty, unit) }}
      {% endfor %}
    </div>
    <button type="button" class="btn secondary" id="add-row" style="margin:6px 0 20px">Add another ingredient</button>
    <div class="row">
      <button class="btn" type="submit">Save recipe</button>
      <a class="btn ghost" href="{{ url_for('recipes.list_view') }}">Cancel</a>
    </div>
  </form>
</div>
<template id="row-template">{{ ing_row() }}</template>
<script>

var rowsEl = document.getElementById('rows');

function initUnit(group) {                      
  var hidden = group.querySelector('.unit-value');
  var m = hidden.value.match(/^\s*(\d*\.?\d*)\s*(.*?)\s*$/);
  if (!m || !hidden.value) return;
  group.querySelector('.unit-num').value = m[1];
  var select = group.querySelector('.unit-select');
  if (m[2]) {
    var found = Array.prototype.some.call(select.options, function (o) { return o.value === m[2]; });
    if (!found) {                                
      var og = document.createElement('optgroup');
      og.label = 'Saved earlier';
      var opt = document.createElement('option');
      opt.value = opt.textContent = m[2];
      og.appendChild(opt);
      select.appendChild(og);
    }
    select.value = m[2];
  }
}
function syncUnit(group) {                       
  var n = group.querySelector('.unit-num').value.trim();
  var u = group.querySelector('.unit-select').value;
  group.querySelector('.unit-value').value = u ? n + u : n;
}
rowsEl.addEventListener('input',  function (e) { var g = e.target.closest('.unit-group'); if (g) syncUnit(g); });
rowsEl.addEventListener('change', function (e) { var g = e.target.closest('.unit-group'); if (g) syncUnit(g); });
document.querySelector('form').addEventListener('submit', function () {
  rowsEl.querySelectorAll('.unit-group').forEach(syncUnit);
});
rowsEl.querySelectorAll('.unit-group').forEach(initUnit);

document.getElementById('add-row').addEventListener('click', function () {
  var tpl = document.getElementById('row-template');
  rowsEl.appendChild(tpl.content.cloneNode(true));
  var added = rowsEl.lastElementChild;
  added.classList.add('row-in');
  var first = added.querySelector('input');
  if (first) first.focus();
});
function removeRow(btn) {
  var row = btn.closest('.ing-row');
  row.classList.add('row-out');
  setTimeout(function () { row.remove(); }, 220);
}
</script>
{% endblock %}
""",

    "recipes.html": r"""{% extends "base.html" %}
{% block content %}
<div class="row" style="justify-content:space-between">
  <h1><span class="title-ico"><i class="fas fa-book-open"></i></span>Recipes</h1>
  <div class="row">
    <a class="btn ghost" href="{{ request.script_root }}{{ request.path }}" onclick="location.reload(); return false;"><i class="fas fa-rotate"></i> Refresh</a>
    <a class="btn" href="{{ url_for('recipes.new_recipe') }}">New recipe</a>
  </div>
</div>
<p class="sub">Your saved recipes and their ingredients.</p>
{% if not recipes %}
<div class="card"><p class="muted">No recipes yet. Add one to start checking your pantry.</p></div>
{% endif %}
{% for r in recipes %}
<div class="card list-item" style="flex-direction:column;align-items:stretch">
  <div class="row" style="justify-content:space-between">
    <div>
      <strong>{{ r.row.recipe_name }}</strong>
      <div class="muted">Serves {{ r.row.servings }} &middot; {{ r.ingredient_names | join(', ') }}</div>
    </div>
    <div class="row">
      <a class="btn secondary" href="{{ url_for('recipes.edit_recipe', recipe_id=r.row.recipe_id) }}">Edit</a>
      <form action="{{ url_for('recipes.delete', recipe_id=r.row.recipe_id) }}" method="post">
        <button class="btn danger" type="submit">Delete</button>
      </form>
    </div>
  </div>
</div>
{% endfor %}
{% include '_back.html' %}
{% endblock %}
""",

    "shopping_list.html": r"""{% extends "base.html" %}
{% block content %}
<h1>Shopping list</h1>
<p class="sub">For {{ data.label }}.</p>
<div class="card">
  <table>
    <tr><th>Ingredient</th><th>Amount needed</th></tr>
    {% for i in data.rows %}
    <tr>
      <td>{{ i.ingredient_name }}{% if i.needed_for %}<div class="muted small tight">for {{ i.needed_for }}</div>{% endif %}</td>
      <td>{{ i.quantity }} {{ i.unit }}</td>
    </tr>
    {% endfor %}
  </table>
</div>
<div class="card">
  <strong>Have you bought the missing ingredients?</strong>
  <p class="muted">Enter how much you bought and it will be added to your pantry.</p>
  <form method="post" action="{{ url_for('check.purchase') }}">
    {% for i in data.rows %}
    <div class="field">
      <label>{{ i.ingredient_name }}{% if i.unit %} ({{ i.unit }}){% endif %}</label>
      <input type="text" name="qty_{{ loop.index0 }}" inputmode="decimal" value="{{ i.quantity }}">
    </div>
    {% endfor %}
    <button class="btn" type="submit">Add to pantry and check again</button>
  </form>
</div>
{% include '_back.html' %}
{% endblock %}
""",

    "signup.html": r"""{% extends "base.html" %}
{% block wrapclass %}narrow{% endblock %}
{% block content %}
<div class="card">
  <h1>Create your account</h1>
  <p class="sub">Save your pantry and recipes so they are ready when you shop.</p>
  <form method="post">
    <div class="field"><label for="name">Full name</label>
      <input id="name" name="name" type="text" value="{{ values.name or '' }}"></div>
    <div class="field"><label for="email">Email</label>
      <input id="email" name="email" type="email" value="{{ values.email or '' }}"></div>
    <div class="field"><label for="password">Password</label>
      <input id="password" name="password" type="password"></div>
    <div class="field"><label for="confirm">Confirm password</label>
      <input id="confirm" name="confirm" type="password"></div>
    <button class="btn" type="submit">Create account</button>
  </form>
  <p style="margin-top:14px">Already have an account? <a href="{{ url_for('auth.login') }}">Log in</a></p>
</div>
{% endblock %}
""",

    "error_database.html": r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Database needed - Recipe Pantry System</title>
<link rel="stylesheet" href="{{ url_for('stylesheet', v=css_version) }}">
</head>
<body>
<main>
<div class="wrap narrow">
  <div class="card">
    <h1><span class="title-ico"><i class="fas fa-triangle-exclamation"></i></span>Database needed</h1>
    <p class="sub">The app is running, but it cannot reach its MySQL database.</p>
    <ol class="sub" style="padding-left:20px">
      <li>Open the <strong>XAMPP Control Panel</strong> and press <strong>Start</strong> next to <strong>MySQL</strong>.</li>
      <li>Reload this page. The database and tables are created automatically.</li>
    </ol>
    <details><summary class="muted">Technical detail</summary><pre style="white-space:pre-wrap">{{ message }}</pre></details>
    <p style="margin-top:18px"><a class="btn" href="{{ request.script_root }}{{ request.path }}" onclick="location.reload(); return false;"><i class="fas fa-rotate"></i> Try again</a></p>
  </div>
</div>
</main>
</body>
</html>
""",

}
