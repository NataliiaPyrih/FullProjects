using Microsoft.ML;
using Microsoft.ML.Data;
using static StudentJournal.StudentPerformanceModel;
using StudentJournal.Models;

public static class PredictionModel
{
    private static Lazy<PredictionEngine<ModelInput, StudentPrediction>> _lazyPredictionEngine =
        new Lazy<PredictionEngine<ModelInput, StudentPrediction>>(CreatePredictionEngine);

    private static PredictionEngine<ModelInput, StudentPrediction> _predictionEngine => _lazyPredictionEngine.Value;

    public static float PredictExamScore(Student student)
    {
        if (_predictionEngine == null)
            throw new InvalidOperationException("Prediction engine is not initialized.");
        var modelInput = MapStudentToModelInput(student);

        var prediction = _predictionEngine.Predict(modelInput);
        return prediction.PredictedScore;
    }

    private static PredictionEngine<ModelInput, StudentPrediction> CreatePredictionEngine()
    {
        var mlContext = new MLContext();
        ITransformer model = mlContext.Model.Load("StudentPerformanceModel.mlnet", out var inputSchema);
        return mlContext.Model.CreatePredictionEngine<ModelInput, StudentPrediction>(model);
    }
    private static ModelInput MapStudentToModelInput(Student student)
    {
        return new ModelInput
        {
            Parental_Involvement = student.Parental_Involvement.ToString(),
            Access_to_Resources = student.Access_to_Resources.ToString(),
            Extracurricular_Activities = Convert.ToBoolean(student.Extracurricular_Activities),
            Motivation_Level = student.Motivation_Level.ToString(),
            Internet_Access = Convert.ToBoolean(student.Internet_Access),
            Family_Income = student.Family_Income.ToString(),
            Teacher_Quality = student.Teacher_Quality.ToString(),
            School_Type = student.School_Type.ToString(),
            Peer_Influence = student.Peer_Influence.ToString(),
            Learning_Disabilities = Convert.ToBoolean(student.Learning_Disabilities),
            Parental_Education_Level = student.Parental_Education_Level.ToString(),
            Distance_from_Home = student.Distance_from_Home.ToString(),
            Gender = student.Gender.ToString(),
            Hours_Studied = student.Hours_Studied,
            Attendance = student.Attendance,
            Sleep_Hours = student.Sleep_Hours,
            Previous_Scores = student.Previous_Scores,
            Tutoring_Sessions = student.Tutoring_Sessions,
            Physical_Activity = student.Physical_Activity
        };
    }
}

public class StudentPrediction
{
    [ColumnName("Score")]
    public float PredictedScore { get; set; }
}

public class ModelInput
{
    public float Hours_Studied { get; set; }
    public float Attendance { get; set; }
    public string Parental_Involvement { get; set; }
    public string Access_to_Resources { get; set; }
    public bool Extracurricular_Activities { get; set; }
    public float Sleep_Hours { get; set; }
    public float Previous_Scores { get; set; }
    public string Motivation_Level { get; set; }
    public bool Internet_Access { get; set; }
    public float Tutoring_Sessions { get; set; }
    public string Family_Income { get; set; }
    public string Teacher_Quality { get; set; }
    public string School_Type { get; set; }
    public string Peer_Influence { get; set; }
    public float Physical_Activity { get; set; }
    public bool Learning_Disabilities { get; set; }
    public string Parental_Education_Level { get; set; }
    public string Distance_from_Home { get; set; }
    public string Gender { get; set; }
}