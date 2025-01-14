using System.Formats.Asn1;
using System.Globalization;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using CsvHelper;
using CsvHelper.Configuration;
using StudentJournal.Models;

namespace StudentJournal.Models
{
    public class StudentRepository
    {
        private static List<Student> Students = new List<Student>();
        private const string CsvFilePath = "Data/StudentSample.csv";

        private static void LoadFromCsv()
        {
            if (!File.Exists(CsvFilePath))
            {
                Console.WriteLine("CSV file not found. Starting with an empty list.");
                return;
            }

            using (var reader = new StreamReader(CsvFilePath))
            using (var csv = new CsvReader(reader, CultureInfo.InvariantCulture))
            {
                Students = csv.GetRecords<Student>().ToList();
            }
        }

        private static void SaveToCsv()
        {
            using (var writer = new StreamWriter(CsvFilePath))
            using (var csv = new CsvWriter(writer, CultureInfo.InvariantCulture))
            {
                csv.WriteRecords(Students);
            }
        }

        public static void InitializeData()
        {
            LoadFromCsv();

            if (Students.Count == 0)
            {
                Console.WriteLine("No data loaded. Generating sample data...");
                GenerateSampleData(20);
                SaveToCsv();
            }
        }
        private static void GenerateSampleData(int count)
        {
            var random = new Random();

            for (int i = 0; i < count; i++)
            {
                var student = new Student();
                student.Id = i + 1;
                student.FirstName = $"Student{i + 1}";
                student.LastName = $"Last{i + 1}";
                student.Hours_Studied = random.Next(10, 40);
                student.Attendance = random.Next(50, 100);
                student.Sleep_Hours = random.Next(4, 12);
                student.Previous_Scores = random.Next(50, 100);
                student.Tutoring_Sessions = random.Next(0, 10);
                student.Physical_Activity = random.Next(0, 7);
                Students.Add(student);
            }
        }

        public static Student? FindStudentById(int id)
        {
            return Students.FirstOrDefault(s => s.Id == id);
        }

        public static void AddStudent(Student student)
        {
            student.Id = Students.Count > 0 ? Students.Max(s => s.Id) + 1 : 1;
            student.Exam_Score = Convert.ToInt64(PredictionModel.PredictExamScore(student));
            Students.Add(student);
            SaveToCsv();
        }

        public static List<Student> GetAllStudents()
        {
            return Students;
        }

        
        public static bool UpdateStudent(Student updatedStudent)
        {

            var student = FindStudentById(updatedStudent.Id);
            if (student != null)
            { 
                student.FirstName = updatedStudent.FirstName;
                student.LastName = updatedStudent.LastName;
                student.Hours_Studied = updatedStudent.Hours_Studied;
                student.Attendance = updatedStudent.Attendance;
                student.Parental_Involvement = updatedStudent.Parental_Involvement;
                student.Access_to_Resources = updatedStudent.Access_to_Resources;
                student.Extracurricular_Activities = updatedStudent.Extracurricular_Activities;
                student.Sleep_Hours = updatedStudent.Sleep_Hours;
                student.Previous_Scores = updatedStudent.Previous_Scores;
                student.Motivation_Level = updatedStudent.Motivation_Level;
                student.Internet_Access = updatedStudent.Internet_Access;
                student.Tutoring_Sessions = updatedStudent.Tutoring_Sessions;
                student.Family_Income = updatedStudent.Family_Income;
                student.Teacher_Quality = updatedStudent.Teacher_Quality;
                student.School_Type = updatedStudent.School_Type;
                student.Peer_Influence = updatedStudent.Peer_Influence;
                student.Physical_Activity = updatedStudent.Physical_Activity;
                student.Learning_Disabilities = updatedStudent.Learning_Disabilities;
                student.Parental_Education_Level = updatedStudent.Parental_Education_Level;
                student.Distance_from_Home = updatedStudent.Distance_from_Home;
                student.Gender = updatedStudent.Gender;
                student.Exam_Score = Convert.ToInt64(PredictionModel.PredictExamScore(student));

                SaveToCsv();        
                return true;
            }

            Console.WriteLine("The student for the update was not found");
            return false;
        }

        public static bool DeleteStudent(int id)
        {
            var student = FindStudentById(id);
            if (student != null)
            {
                Students.Remove(student);
                SaveToCsv();
                return true;
            }
            return false;
        }

        public static float CalculateScore(Student student)
        {
            student.Exam_Score = Convert.ToInt32(PredictionModel.PredictExamScore(student));
            return student.Exam_Score;
        }
    }
}
