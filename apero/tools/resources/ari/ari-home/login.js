function openModal() {
  document.getElementById("loginModal").style.display = "block";
}

function closeModal() {
  document.getElementById("loginModal").style.display = "none";
}


function login() {
  var username = document.getElementById("uname").value;
  var password = document.getElementById("psw").value;

  fetch('user_credentials.json')
    .then(response => response.json())
    .then(users => {
      const user = users.find(u => u.username === username && u.password === hashPassword(password));

    if (user) {
        localStorage.setItem("loggedInUser", username);
	
	localStorage.setItem("loggedInGroup",user["group"]);

        alert("Login successful");
	closeModal();
	updateLoginButtonText();
	ListPages();
        // Redirect to another page after successful login if needed
      } else {
        console.log("Invalid username="+username);
        alert("Invalid username or password");
      }
    })
    .catch(error => console.error('Error loading user credentials:', error));
}

// Use https://codepen.io/watsize/pen/QBzBjM to generate
function hashPassword(password) {
	return CryptoJS.SHA256(password).toString(CryptoJS.enc.Hex);
}


function logout() {
	localStorage.clear();
	updateLoginButtonText();
	ListPages();
	console.log('loggedInUser='+localStorage.getItem("loggedInUser"));
}


// Function to update the text next to the login button
function updateLoginButtonText() {

  const loggedInUser = localStorage.getItem("loggedInUser");
  var loginButton = document.getElementById("loginButton");
  if (loggedInUser) {
    loginButton.innerText = "Logged in as " + loggedInUser;
  } else {
    loginButton.innerText = "Login";
  }
}


// Page access function
function pageAccess(group, index_path) {

	EnableContent();

        // Check if the user is logged in
        const loggedInUser = localStorage.getItem("loggedInUser");
	const loggedInGroup = localStorage.getItem("loggedInGroup");

        if (!loggedInUser) {
            alert("Access denied. You are not logged in.");
            // Redirect to login page or another page
            window.location.href = index_path;
        } else if (!(loggedInGroup.includes(group))) {
            alert("Access denied. You do not have permission to view the "+group+" page.");
            // Redirect to login page or another page
            window.location.href = index_path;
        }
}


// Enable content if javascript is enabled
function EnableContent() {
	document.body.style.display = 'block';
}


// Main login functionality

function mainLogin() {

	EnableContent();

	// Call the function initially to set the initial state
	updateLoginButtonText();

	/*// Get the modal
	var modal = document.getElementById('loginModal')
	// When the user clicks anywhere outside of the moal, close it
	window.onclick = function(event) {
	    if (event.target == modal) {
		modal.style.display = "none";
	    }
	}*/

	// Function to handle form submission when Enter key is pressed
	document.getElementById("loginForm").addEventListener("keydown", function(event) {
	  if (event.key === "Enter") {
	    event.preventDefault(); // Prevent default form submission behavior
	    login(); // Call the login function
	  }
	});
}



function ListPages() {
	const loggedInGroup = localStorage.getItem("loggedInGroup");
	// get the list
        var menuItems = document.querySelectorAll('#pagemenu li');
	// get the div for not being logged in
        var notLoggedIn = document.getElementById('notloggedin');

        // Loop through each list item
	menuItems.forEach(function(item) {
		// Check if the item should be visible based on the id
        	var itemId = item.getAttribute('id')
		// deal with no loggedInGroup
        	if (!loggedInGroup) {
			item.style.display = 'none';
		} else if (loggedInGroup.includes(itemId)) {
			item.style.display = 'block';
		} else {
			item.style.display = 'none';
		};

	});

	//  Display a message if not logged in
	if (!loggedInGroup) {
		notLoggedIn.innerText = 'No pages to view. Please log in.';
	} else {
		notLoggedIn.innerText = '';
	};
	


}

