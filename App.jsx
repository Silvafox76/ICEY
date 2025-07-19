import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './hooks/useAuth.jsx';
import Layout from './components/Layout';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  console.log("ProtectedRoute - isAuthenticated:", isAuthenticated, "loading:", loading);
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  return isAuthenticated ? children : <Navigate to="/login" />;
};

// Public Route Component (redirects to dashboard if authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  console.log("PublicRoute - isAuthenticated:", isAuthenticated, "loading:", loading);
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  return isAuthenticated ? <Navigate to="/" /> : children;
};

function AppContent() {
  return (
    <Router>
      <Routes>
        <Route 
          path="/login" 
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          } 
        />
        <Route 
          path="/" 
          element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/inventory" 
          element={
            <ProtectedRoute>
              <Layout>
                <div className="text-center py-12">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">Inventory Management</h2>
                  <p className="text-gray-600">Inventory management features coming soon...</p>
                </div>
              </Layout>
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/jobs" 
          element={
            <ProtectedRoute>
              <Layout>
                <div className="text-center py-12">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">Job Management</h2>
                  <p className="text-gray-600">Job management features coming soon...</p>
                </div>
              </Layout>
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/reports" 
          element={
            <ProtectedRoute>
              <Layout>
                <div className="text-center py-12">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">Reports & Analytics</h2>
                  <p className="text-gray-600">Reporting features coming soon...</p>
                </div>
              </Layout>
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/users" 
          element={
            <ProtectedRoute>
              <Layout>
                <div className="text-center py-12">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">User Management</h2>
                  <p className="text-gray-600">User management features coming soon...</p>
                </div>
              </Layout>
            </ProtectedRoute>
          } 
        />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
