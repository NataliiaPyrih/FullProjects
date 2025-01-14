using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using StudentJournal.Models;
using static Plotly.NET.StyleParam.DrawingStyle;

namespace StudentJournal.Models
{
    public class UserStore
    {
        private List<User> _users;

        public UserStore()
        {
            var jsonData = File.ReadAllText("Data/users.json");
            _users = JsonSerializer.Deserialize<List<User>>(jsonData);
        }

        public Dictionary<string, string> GetUsers()
        {
            var userDict = new Dictionary<string, string>();
            foreach (var user in _users)
            {
                userDict[user.Username] = user.Password;
            }
            return userDict;
        }
        public string GetUserRole(string username)
        {
            var user = _users.Find(u => u.Username == username);
            return user?.Role;
        }
        public User ValidateUser(string username, string password)
        {
            return _users.FirstOrDefault(u => u.Username == username && u.Password == password);
        }
        public void AddUser(User newUser)
        {
            if (_users.Any(u => u.Username == newUser.Username))
            {
                throw new InvalidOperationException("User already exists.");
            }
            _users.Add(newUser);

            var jsonData = JsonSerializer.Serialize(_users, new JsonSerializerOptions { WriteIndented = true });
            File.WriteAllText("Data/users.json", jsonData);
        }
    }

    public class User
    {
        public string Username { get; set; }
        public string Password { get; set; }
        public string Role { get; set; }
        
    }
}