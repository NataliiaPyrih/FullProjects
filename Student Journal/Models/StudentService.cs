namespace StudentJournal.Models
{
    public class StudentService: IStudentService
    {
        public StudentService()
        {
            StudentRepository.InitializeData();
        }
        public List<Student> GetAllStudents()
        {
            return StudentRepository.GetAllStudents();
        }

        public Student? FindStudentById(int id)
        {
            return StudentRepository.FindStudentById(id);
        }
        public void AddStudent(Student student)
        {
            StudentRepository.AddStudent(student);
        }

        public static bool UpdateStudent(Student updatedStudent)
        {
            return StudentRepository.UpdateStudent(updatedStudent);
        }

        public bool DeleteStudent(int id)
        {
            return StudentRepository.DeleteStudent(id);
        }

        public static float CalculateScore(Student student)
        {
            return StudentRepository.CalculateScore(student);
        }
    }
}
