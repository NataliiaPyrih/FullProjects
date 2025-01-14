namespace StudentJournal.Models
{
    public interface IStudentService
    {
        List<Student> GetAllStudents();
        Student? FindStudentById(int id);
        void AddStudent(Student student);
        bool DeleteStudent(int id);

    }
}
