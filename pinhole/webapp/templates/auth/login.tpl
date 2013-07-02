{% extends "base.tpl" %}

{% block content %}
<div class="content">
  <div class="row">
    <div class="login-form text-center">
      <h2>Login</h2>
      <form action="">
        <fieldset>
          <div class="clearfix">
            <input type="text" name="username" placeholder="Username">
          </div>
          <div class="clearfix">
            <input type="password" name="password" placeholder="Password">
          </div>
          <button class="btn btn-primary" type="submit">Sign in</button>
          <a href="/account/password_reset" class="forgot">Forgot your password?</a>
        </fieldset>
      </form>
       No account? <a href="/account/signup" class="register">Register now!</a>
    </div>
  </div>
</div>
{% endblock %}
