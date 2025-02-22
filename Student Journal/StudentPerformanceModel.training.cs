﻿// This file was auto-generated by ML.NET Model Builder.
using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.ML;
using Microsoft.ML.Data;
using Microsoft.ML.Trainers;
using Microsoft.ML.Trainers.LightGbm;
using Microsoft.ML.Transforms;

namespace StudentJournal
{
    public partial class StudentPerformanceModel
    {
        public const string RetrainFilePath =  @"E:\Документы\програмування під .Net Core\Пз 3\StudentPerformanceModel\StudentPerformanceModel\Data\StudentDataset.csv";
        public const char RetrainSeparatorChar = ',';
        public const bool RetrainHasHeader =  true;
        public const bool RetrainAllowQuoting =  false;

         /// <summary>
        /// Train a new model with the provided dataset.
        /// </summary>
        /// <param name="outputModelPath">File path for saving the model. Should be similar to "C:\YourPath\ModelName.mlnet"</param>
        /// <param name="inputDataFilePath">Path to the data file for training.</param>
        /// <param name="separatorChar">Separator character for delimited training file.</param>
        /// <param name="hasHeader">Boolean if training file has a header.</param>
        public static void Train(string outputModelPath, string inputDataFilePath = RetrainFilePath, char separatorChar = RetrainSeparatorChar, bool hasHeader = RetrainHasHeader, bool allowQuoting = RetrainAllowQuoting)
        {
            var mlContext = new MLContext();

            var data = LoadIDataViewFromFile(mlContext, inputDataFilePath, separatorChar, hasHeader, allowQuoting);
            var model = RetrainModel(mlContext, data);
            SaveModel(mlContext, model, data, outputModelPath);
        }

        /// <summary>
        /// Load an IDataView from a file path.
        /// </summary>
        /// <param name="mlContext">The common context for all ML.NET operations.</param>
        /// <param name="inputDataFilePath">Path to the data file for training.</param>
        /// <param name="separatorChar">Separator character for delimited training file.</param>
        /// <param name="hasHeader">Boolean if training file has a header.</param>
        /// <returns>IDataView with loaded training data.</returns>
        public static IDataView LoadIDataViewFromFile(MLContext mlContext, string inputDataFilePath, char separatorChar, bool hasHeader, bool allowQuoting)
        {
            return mlContext.Data.LoadFromTextFile<ModelInput>(inputDataFilePath, separatorChar, hasHeader, allowQuoting: allowQuoting);
        }


        /// <summary>
        /// Save a model at the specified path.
        /// </summary>
        /// <param name="mlContext">The common context for all ML.NET operations.</param>
        /// <param name="model">Model to save.</param>
        /// <param name="data">IDataView used to train the model.</param>
        /// <param name="modelSavePath">File path for saving the model. Should be similar to "C:\YourPath\ModelName.mlnet.</param>
        public static void SaveModel(MLContext mlContext, ITransformer model, IDataView data, string modelSavePath)
        {
            // Pull the data schema from the IDataView used for training the model
            DataViewSchema dataViewSchema = data.Schema;

            using (var fs = File.Create(modelSavePath))
            {
                mlContext.Model.Save(model, dataViewSchema, fs);
            }
        }


        /// <summary>
        /// Retrain model using the pipeline generated as part of the training process.
        /// </summary>
        /// <param name="mlContext"></param>
        /// <param name="trainData"></param>
        /// <returns></returns>
        public static ITransformer RetrainModel(MLContext mlContext, IDataView trainData)
        {
            var pipeline = BuildPipeline(mlContext);
            var model = pipeline.Fit(trainData);

            return model;
        }

        /// <summary>
        /// build the pipeline that is used from model builder. Use this function to retrain model.
        /// </summary>
        /// <param name="mlContext"></param>
        /// <returns></returns>
        public static IEstimator<ITransformer> BuildPipeline(MLContext mlContext)
        {
            // Data process configuration with pipeline data transformations
            var pipeline = mlContext.Transforms.Categorical.OneHotEncoding(new []{new InputOutputColumnPair(@"Parental_Involvement", @"Parental_Involvement"),new InputOutputColumnPair(@"Access_to_Resources", @"Access_to_Resources"),new InputOutputColumnPair(@"Extracurricular_Activities", @"Extracurricular_Activities"),new InputOutputColumnPair(@"Motivation_Level", @"Motivation_Level"),new InputOutputColumnPair(@"Internet_Access", @"Internet_Access"),new InputOutputColumnPair(@"Family_Income", @"Family_Income"),new InputOutputColumnPair(@"Teacher_Quality", @"Teacher_Quality"),new InputOutputColumnPair(@"School_Type", @"School_Type"),new InputOutputColumnPair(@"Peer_Influence", @"Peer_Influence"),new InputOutputColumnPair(@"Learning_Disabilities", @"Learning_Disabilities"),new InputOutputColumnPair(@"Parental_Education_Level", @"Parental_Education_Level"),new InputOutputColumnPair(@"Distance_from_Home", @"Distance_from_Home"),new InputOutputColumnPair(@"Gender", @"Gender")}, outputKind: OneHotEncodingEstimator.OutputKind.Indicator)      
                                    .Append(mlContext.Transforms.ReplaceMissingValues(new []{new InputOutputColumnPair(@"Hours_Studied", @"Hours_Studied"),new InputOutputColumnPair(@"Attendance", @"Attendance"),new InputOutputColumnPair(@"Sleep_Hours", @"Sleep_Hours"),new InputOutputColumnPair(@"Previous_Scores", @"Previous_Scores"),new InputOutputColumnPair(@"Tutoring_Sessions", @"Tutoring_Sessions"),new InputOutputColumnPair(@"Physical_Activity", @"Physical_Activity")}))      
                                    .Append(mlContext.Transforms.Concatenate(@"Features", new []{@"Parental_Involvement",@"Access_to_Resources",@"Extracurricular_Activities",@"Motivation_Level",@"Internet_Access",@"Family_Income",@"Teacher_Quality",@"School_Type",@"Peer_Influence",@"Learning_Disabilities",@"Parental_Education_Level",@"Distance_from_Home",@"Gender",@"Hours_Studied",@"Attendance",@"Sleep_Hours",@"Previous_Scores",@"Tutoring_Sessions",@"Physical_Activity"}))      
                                    .Append(mlContext.Regression.Trainers.LightGbm(new LightGbmRegressionTrainer.Options(){NumberOfLeaves=4,NumberOfIterations=2562,MinimumExampleCountPerLeaf=20,LearningRate=0.9999997766729865,LabelColumnName=@"Exam_Score",FeatureColumnName=@"Features",Booster=new GradientBooster.Options(){SubsampleFraction=0.9999997766729865,FeatureFraction=0.99999999,L1Regularization=2E-10,L2Regularization=0.23941660914571467},MaximumBinCountPerFeature=215}));

            return pipeline;
        }
    }
 }
