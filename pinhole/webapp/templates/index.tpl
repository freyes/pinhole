{% extends "base.tpl" %}

{% block jslibs %}
<script type="text/javascript" src="/media/js/vendor/jquery.photoset-grid.min.js"></script>
{% endblock %}

{% block content %}
Logged in

<div class="photoset-grid-basic" data-layout="12">
  <img src="http://placehold.it/350x150" data-highres="http://placehold.it/2048x1360">
  <img src="http://placehold.it/350x150" data-highres="http://placehold.it/2048x1360">
  <img src="http://placehold.it/350x150" data-highres="http://placehold.it/2048x1360">
</div>
{% endblock %}