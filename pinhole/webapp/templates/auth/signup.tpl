{% extends "base.tpl" %}


{% block content %}
<form id="frm_signup" action="" method="POST">
  <fieldset>
    <legend>Sign up</legend>
    <label>Email</label>
    <input type="text" name="email" placeholder="Email">

    <label>Username</label>
    <input type="text" name="username" placeholder="Username">

    <label>Password</label>
    <input type="password" name="password_1" placeholder="Password">

    <label>Confirm Password</label>
    <input type="password" name="password_2" placeholder="Confirm Password">

    <label class="checkbox">
      <input type="checkbox" name="tos"> I have read and agree to the Terms of Use
    </label>
    <input type="submit" class="btn btn-primary" value="Submit" >
  </fieldset>
</form>

{% endblock %}