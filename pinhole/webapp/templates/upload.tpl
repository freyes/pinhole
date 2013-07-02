{% extends "base.tpl" %}

{% block jslibs %}
<script type="text/javascript" src="//api.filepicker.io/v1/filepicker.js"></script>
{% endblock %}

{% block javascript %}
<script type="text/javascript" src="/media/js/upload.js"></script>
{% endblock %}

{% block content %}
<em class="btn upload">upload</em>
{% endblock %}