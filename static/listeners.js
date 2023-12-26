// When the page loads, execute the following function
window.addEventListener('load', function(){
  // Get the references to the password input field and the checkbox
  var current_password = document.getElementById('password');
  var show_password = document.getElementById('check');

  // Add an event listener to the checkbox to handle its change event
  show_password.addEventListener('change', function(){
    // If the checkbox is checked
    if(this.checked) {
      // Set the type of the password input field to 'text'
      current_password.type = 'text';
    } else {
      // Set the type of the password input field back to 'password'
      current_password.type = 'password';
    }
  });
});