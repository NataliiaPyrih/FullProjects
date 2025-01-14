using Microsoft.AspNetCore.Mvc;
using StudentJournal.Models;

namespace StudentJournal.Controllers
{
    public interface IStudentController
    {
        IActionResult Index();
        IActionResult AccessDenied();
        IActionResult StudentsView();
        IActionResult Debtors();
        IActionResult Details(int id);
        IActionResult Add();
        IActionResult Add(Student newStudent);
        IActionResult CalculateScoreAjax(Student student);
        IActionResult UpdateStudent(Student updatedStudent);
        IActionResult UpdateStudentAjax(Student updatedStudent);
        IActionResult DeleteStudentAjax(int id);
    }
}
