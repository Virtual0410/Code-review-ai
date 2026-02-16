"""
Example Buggy Code for Testing
This file contains intentional issues for each language analyzer
"""

# ============================================
# PYTHON EXAMPLES
# ============================================

def calculate_average(numbers=[]):  # Mutable default argument
    """Calculate average - has bugs"""
    total = 0
    for num in numbers:
        total = total + num
    return total / len(numbers)  # Division by zero if empty

def get_user_data(user_id):
    """Fetch user - SQL injection vulnerability"""
    query = "SELECT * FROM users WHERE id = " + user_id
    return execute_query(query)

def process_input(user_input):
    """Process input - dangerous eval()"""
    result = eval(user_input)
    return result

# Hardcoded credentials
API_KEY = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
DATABASE_PASSWORD = "admin123"

def load_file(filename):
    """Load file - no error handling"""
    f = open(filename)  # Should use 'with' statement
    data = f.read()
    return data

# Bad exception handling
try:
    risky_operation()
except:  # Bare except - too broad
    pass

# ============================================
# JAVASCRIPT EXAMPLES
# ============================================

"""
// Using var instead of const/let
var globalVar = "bad practice";

// XSS vulnerability
function displayUser(userData) {
    document.getElementById('user').innerHTML = userData.name;
}

// eval() usage
function calculate(expression) {
    return eval(expression);
}

// Hardcoded secret
const apiKey = "sk-secret-123456";

// Using == instead of ===
if (value == null) {
    // Should use ===
}

// No Promise error handling
fetch('/api/data')
    .then(response => response.json())
    .then(data => console.log(data));
    // Missing .catch()

// Callback hell
getData(function(a) {
    getMoreData(a, function(b) {
        getMoreData(b, function(c) {
            getMoreData(c, function(d) {
                // Pyramid of doom
            });
        });
    });
});
"""

# ============================================
# JAVA EXAMPLES
# ============================================

"""
public class BuggyCode {
    // Hardcoded password
    private static final String PASSWORD = "admin123";
    
    // SQL injection
    public User getUser(String userId) {
        String query = "SELECT * FROM users WHERE id = " + userId;
        return executeQuery(query);
    }
    
    // String comparison with ==
    public boolean checkName(String name) {
        return name == "admin";  // Should use .equals()
    }
    
    // Not closing resources
    public String readFile(String path) throws IOException {
        FileInputStream fis = new FileInputStream(path);
        // Should use try-with-resources
        byte[] data = new byte[fis.available()];
        fis.read(data);
        return new String(data);
    }
    
    // Catching generic Exception
    public void riskyOperation() {
        try {
            // Some risky code
        } catch (Exception e) {  // Too broad
            e.printStackTrace();
        }
    }
}
"""

# ============================================
# Common to All Languages
# ============================================

# More Python issues for demonstration

class DataProcessor:
    def __init__(self):
        self.secret_key = "my-secret-key-12345"  # Hardcoded
        self.db_pass = "password123"  # Hardcoded
    
    def process(self, items):
        results = []
        for i in range(len(items)):  # Should use enumerate
            results.append(items[i] * 2)
        return results

def unsafe_deserialize(data):
    """Unsafe pickle usage"""
    import pickle
    return pickle.loads(data)  # Dangerous with untrusted data

# Global variable
config = {"debug": True}  # Should avoid global state

def poor_error_handling():
    """No error handling"""
    file = open("important.txt")
    data = file.read()
    # File never closed!
    return data

print("This file contains intentional bugs for testing!")
print("Load it in the GUI to see all the issues detected.")
