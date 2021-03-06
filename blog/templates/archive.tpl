{% extends '__layout.tpl' %}

{% block meta_tags %}
  {{ block.super }}
  <meta name="description"
        content="Posts created in {{date}}" />
{% endblock %}

{% block title %}
  Posts | {{ date }}
{% endblock %}

{% block container %}
  <div class="row">
    <div class="col-md-3 col-md-offset-1">
      {% include '_archive-tree.tpl' %}
    </div>
    <div class="col-md-7">
      <h4>Posts in {{ date }}</h4>
      {% include '_blog-list.tpl' %}
    </div>
  </div>
{% endblock %}
