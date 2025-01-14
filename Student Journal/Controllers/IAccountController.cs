using Microsoft.AspNetCore.Mvc;

namespace StudentJournal.Controllers
{
    public interface IAccountController
    {
        IActionResult Login();
        IActionResult Login(string username, string password);
        IActionResult Logout();
        IActionResult SignUp();
        IActionResult Register(string username, string password, string role);
    }
}
