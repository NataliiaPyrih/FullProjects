using Microsoft.AspNetCore.Mvc;
using StudentJournal.Models;
using static Plotly.NET.StyleParam.DrawingStyle;
using System.Text.Json;

namespace StudentJournal.Controllers
{
    public class AccountController : Controller, IAccountController
    {
        private readonly UserStore _userStore;

        public AccountController(UserStore userStore)
        {
            _userStore = userStore;
        }

        [HttpGet]
        public IActionResult Login()
        {
            return View();
        }

        [HttpPost]
        public IActionResult Login(string username, string password)
        {
            var user = _userStore.ValidateUser(username, password);
            if (user != null)
            {
                HttpContext.Session.SetString("Role", user.Role);
                return RedirectToAction("Index", "Student");
            }

            ViewBag.ErrorMessage = "Incorrect login details";
            return View();
        }

        [HttpPost]
        public IActionResult Logout()
        {
            HttpContext.Session.Remove("Role");
            return RedirectToAction("Index", "Student");
        }

        [HttpGet]
        public IActionResult SignUp()
        {
            return View("SignUp");
        }

        // POST: /Account/SignUp
        [HttpPost]
        public IActionResult Register(string username, string password, string role)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(username) || string.IsNullOrWhiteSpace(password))
                {
                    ViewBag.ErrorMessage = "Username and Password are required.";
                    return View("SignUp");
                }

                var newUser = new StudentJournal.Models.User
                {
                    Username = username,
                    Password = password,
                    Role = role
                };

                _userStore.AddUser(newUser);

                ViewBag.SuccessMessage = "Registration successful. You can now log in.";
                return View("SignUp");
            }
            catch (InvalidOperationException ex)
            {
                ViewBag.ErrorMessage = ex.Message;
                return View("SignUp");
            }
            catch (Exception)
            {
                ViewBag.ErrorMessage = "An error occurred. Please try again.";
                return View("SignUp");
            }
        }
    }
}