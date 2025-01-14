using Microsoft.AspNetCore.Mvc;
using Microsoft.ML;
using StudentJournal.Attributes;
using StudentJournal.Models;
using System.Text.Json.Serialization;
using System.Text.Json;

namespace StudentJournal.Controllers
{
    public class StudentController : Controller, IStudentController
    {
        private readonly IStudentService _studentService;

        public StudentController(IStudentService studentService)
        {
            _studentService = studentService;
        }
        [HttpGet]
        public IActionResult Index()
        {
            ViewData["IsLoggedIn"] = HttpContext.Session.GetString("Role") != null;
            return View(new Student()); 
        }
        public IActionResult AccessDenied()
        {
            ViewData["IsLoggedIn"] = HttpContext.Session.GetString("Role") != null;
            return View();
        }

        [AuthorizeRole("Curator")]
        [HttpGet]
        public IActionResult StudentsView()
        {
            var students = _studentService.GetAllStudents();
            return View(students);
        }

        [AuthorizeRole("Curator", "StudentLeader")]
        [HttpGet]
        public IActionResult Debtors()
        {
            var debtors = _studentService.GetAllStudents().Where(s => s.Exam_Score < 75).ToList();
            return View(debtors);
        }


        [AuthorizeRole("Curator")]
        public IActionResult Details(int id)
        {
            var student = _studentService.FindStudentById(id);

            if (student == null)
            {
                return NotFound();
            }

            return View(student);
        }

        [AuthorizeRole("Curator")]
        public IActionResult Add()
        {
            var newStudent = new Student();
            return View(newStudent);
        }

        [AuthorizeRole("Curator")]
        [HttpPost]
        public IActionResult Add(Student newStudent)
        {
            if (ModelState.IsValid)
            {
                _studentService.AddStudent(newStudent);
                return RedirectToAction("StudentsView");
            }
            return View(newStudent);
        }

        [HttpPost]
        public IActionResult CalculateScoreAjax(Student student)
        {
            try
            {
                int score = Convert.ToInt32(StudentService.CalculateScore(student));

                string message = score > 65
                    ? $"Congratulations! Your score: {score}"
                    : $"Your score: {score}. You still have time. Try to improve your result.";

                bool isSuccess = score > 65;

                return Json(new { isSuccess, message });
            }
            catch (Exception ex)
            {
                return Json(new { isSuccess = false, message = "Ошибка: " + ex.Message });
            }
        }

        [AuthorizeRole("Curator")]
        [HttpPost]
        public IActionResult UpdateStudent(Student updatedStudent)
        {
            if (ModelState.IsValid)
            {
                bool result = StudentService.UpdateStudent(updatedStudent);
                Console.WriteLine(result);
                Console.WriteLine(updatedStudent);
                if (result)
                {

                    return RedirectToAction("Index"); 
                }

                return View("Details", updatedStudent);
            }
            return RedirectToAction("Index");
        }

        [AuthorizeRole("Curator")]
        [HttpPost]
        public IActionResult UpdateStudentAjax(Student updatedStudent)
        {
            if (ModelState.IsValid)
            {
                try
                {
                    bool result = StudentService.UpdateStudent(updatedStudent);

                    if (result)
                    {
                        var updatedStudentFromRepo = _studentService.FindStudentById(updatedStudent.Id);

                        return Json(new { success = true, examScore = updatedStudentFromRepo.Exam_Score });
                    }
                    else
                    {
                        return Json(new { success = false, message = "Failed to update the student's data." });
                    }
                }
                catch (Exception ex)
                {
                    return Json(new { success = false, message = $"Error: {ex.Message}" });
                }
            }

            return Json(new { success = false, message = "Data from these form are invalid" });
        }

        [AuthorizeRole("Curator")]
        [HttpPost]
        public IActionResult DeleteStudentAjax(int id)
        {
           
            try
            {
                bool result = _studentService.DeleteStudent(id);

                if (result)
                {
                    return Json(new { success = true });
                }
                else
                {
                    return Json(new { success = false, message = "Failed to remove student." });
                }
            }
            catch (Exception ex)
            {

                return Json(new { success = false, message = $"Error: {ex.Message}" });
            }
        }

        [HttpGet]
        public IActionResult GetSortedStudents(string sortField, string sortOrder, bool isDebtor = false)
        {
            List<Student> students = _studentService.GetAllStudents();

            if (isDebtor)
            {
                students = students.Where(s => s.Exam_Score < 75).ToList();
            }

            if (sortField == "ExamScore")
            {
                students = sortOrder == "asc"
                    ? students.OrderBy(s => s.Exam_Score).ToList()
                    : students.OrderByDescending(s => s.Exam_Score).ToList();
            }

            var result = students.Select(s => new
            {
                s.Id,
                s.FirstName,
                s.LastName,
                s.Hours_Studied,
                s.Attendance,
                Extracurricular_Activities = s.Extracurricular_Activities.ToString(),
                s.Sleep_Hours,
                s.Previous_Scores,
                Internet_Access = s.Internet_Access.ToString(),
                s.Tutoring_Sessions,
                School_Type = s.School_Type.ToString(),
                s.Physical_Activity,
                Gender = s.Gender.ToString(),
                s.Exam_Score
            });

            return Json(result);
        }


    }
}
