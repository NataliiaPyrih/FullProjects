using Microsoft.ML.Data;
using System.ComponentModel.DataAnnotations;

namespace StudentJournal.Models
{
    public class Student
    {
        public int Id { get; set; }
        [Required(ErrorMessage = "First Name is required")]
        public string FirstName { get; set; }
        [Required(ErrorMessage = "Last Name is required")]
        public string LastName { get; set; }

        [LoadColumn(0)]
        [Range(0, int.MaxValue, ErrorMessage = "Value cannot be less than 0.")]
        public int Hours_Studied { get; set; }
        [LoadColumn(1)]
        [Range(0, 100, ErrorMessage = "Attendance must be between 0 and 100.")]
        public int Attendance { get; set; }
        [LoadColumn(2)]
        public CategoryLevel Parental_Involvement { get; set; }
        [LoadColumn(3)]
        public CategoryLevel Access_to_Resources { get; set; }
        [LoadColumn(4)]
        public ChooseValue Extracurricular_Activities { get; set; }
        [LoadColumn(5)]
        [Range(0, 24, ErrorMessage = "Sleep Hours must be between 0 and 24")]
        public int Sleep_Hours { get; set; }
        [LoadColumn(6)]
        [Range(0, 100, ErrorMessage = "Previous Score must be between 0 and 100.")]
        public int Previous_Scores { get; set; }
        [LoadColumn(7)]
        public CategoryLevel Motivation_Level { get; set; }
        [LoadColumn(8)]
        public ChooseValue Internet_Access { get; set; }
        [LoadColumn(9)]
        [Range(0, 30, ErrorMessage = "Number of Tutoring Sessions must be between 0 and 30.")]
        public int Tutoring_Sessions { get; set; }
        [LoadColumn(10)]
        public CategoryLevel Family_Income { get; set; }
        [LoadColumn(11)]
        public CategoryLevel Teacher_Quality { get; set; }
        [LoadColumn(12)]
        public SchoolType School_Type { get; set; }
        [LoadColumn(13)]
        public PeerInfluence Peer_Influence { get; set; }
        [LoadColumn(14)]
        [Range(0, 50, ErrorMessage = "Number of Physical_Activity lessons must be between 0 and 50.")]
        public int Physical_Activity { get; set; }
        [LoadColumn(15)]
        public ChooseValue Learning_Disabilities { get; set; }
        [LoadColumn(16)]
        public ParenteducationLevel Parental_Education_Level { get; set; }
        [LoadColumn(17)]
        public Distance_from_Home Distance_from_Home { get; set; }
        [LoadColumn(18)]
        public Gender Gender { get; set; }

        [Range(0, 100, ErrorMessage = "Exam Score must be between 0 and 100")]
        [NoColumn]
        public float Exam_Score { get; set; }

        public Student()
        {
            Parental_Involvement = CategoryLevel.Low;
            Access_to_Resources = CategoryLevel.Low;
            Extracurricular_Activities = ChooseValue.No;
            Motivation_Level = CategoryLevel.Low;
            Internet_Access = ChooseValue.No;
            Family_Income = CategoryLevel.Low;
            Teacher_Quality = CategoryLevel.Low;
            School_Type = SchoolType.Public;
            Peer_Influence = PeerInfluence.Negative;
            Learning_Disabilities = ChooseValue.No;
            Parental_Education_Level = ParenteducationLevel.HighSchool;
            Distance_from_Home = Distance_from_Home.Moderate;
        }

    }
    public enum CategoryLevel
    {
        Low,
        Medium,
        High
    }
    public enum SchoolType
    {
        Public,
        Private
    }
    public enum ParenteducationLevel
    {
        [Display(Name = "High School")]
        HighSchool,
        College,
        Postgraduate
    }
    public enum Distance_from_Home
    {
        Near,
        Moderate,
        Far
    }
    public enum PeerInfluence
    {
        Negative,
        Neutral,
        Positive
    }
    public enum Gender
    {
        Male,
        Female
    }
    public enum ChooseValue
    {
        No,
        Yes
    }
    public static class EnumMapper
    {
        private static readonly Dictionary<string, ParenteducationLevel> ParentalEducationMapping =
            new Dictionary<string, ParenteducationLevel>(StringComparer.OrdinalIgnoreCase)
            {
            { "High School", ParenteducationLevel.HighSchool },
            { "College", ParenteducationLevel.College },
            { "Postgraduate", ParenteducationLevel.Postgraduate }
            };

        public static ParenteducationLevel MapParentalEducation(string value)
        {
            if (ParentalEducationMapping.TryGetValue(value, out var result))
            {
                return result;
            }
            throw new ArgumentException($"Unknown Parental Education Level: {value}");
        }
    }
}
