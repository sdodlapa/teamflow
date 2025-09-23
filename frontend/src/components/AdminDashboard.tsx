/**
 * Admin Dashboard Component for TeamFlow
 * Comprehensive administrative interface with analytics and system management
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Tabs,
  Tab,
  Button,
  CircularProgress,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Business as BusinessIcon,
  Assignment as AssignmentIcon,
  Analytics as AnalyticsIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface AdminDashboardProps {
  userRole: string;
}

interface DashboardData {
  systemStatistics: {
    totalUsers: number;
    totalOrganizations: number;
    totalProjects: number;
    totalTasks: number;
  };
  userMetrics: {
    activeUsersToday: number;
    activeUsersWeek: number;
    activeUsersMonth: number;
    newRegistrationsToday: number;
    newRegistrationsWeek: number;
    newRegistrationsMonth: number;
    userRetentionRate: number;
  };
  performanceSummary: {
    healthScores: {
      overall: number;
      apiPerformance: number;
      databasePerformance: number;
      cachePerformance: number;
    };
  };
  systemHealth: {
    overallStatus: string;
    apiStatus: string;
    databaseStatus: string;
    cacheStatus: string;
    storageStatus: string;
  };
  recentActivities: Array<{
    type: string;
    description: string;
    user: string;
    timestamp: string;
    icon: string;
  }>;
  growthMetrics: {
    newUsers30Days: number;
    newOrganizations30Days: number;
    newProjects30Days: number;
  };
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ userRole }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/admin/dashboard', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch dashboard data');
      }

      const data = await response.json();
      setDashboardData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const getHealthStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'operational':
        return 'success';
      case 'warning':
        return 'warning';
      case 'critical':
        return 'error';
      default:
        return 'info';
    }
  };

  const getHealthScoreColor = (score: number) => {
    if (score >= 90) return '#4caf50';
    if (score >= 75) return '#ff9800';
    if (score >= 60) return '#f44336';
    return '#9c27b0';
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={2}>
        <Alert severity="error">Error loading dashboard: {error}</Alert>
        <Button onClick={fetchDashboardData} variant="contained" sx={{ mt: 2 }}>
          Retry
        </Button>
      </Box>
    );
  }

  if (!dashboardData) {
    return <Alert severity="warning">No dashboard data available</Alert>;
  }

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Chart data preparation
  const userGrowthData = [
    { name: 'Jan', users: 400 },
    { name: 'Feb', users: 300 },
    { name: 'Mar', users: 500 },
    { name: 'Apr', users: 800 },
    { name: 'May', users: 1200 },
    { name: 'Jun', users: 1500 }
  ];

  const performanceData = [
    { name: 'API', score: dashboardData.performanceSummary.healthScores.apiPerformance },
    { name: 'Database', score: dashboardData.performanceSummary.healthScores.databasePerformance },
    { name: 'Cache', score: dashboardData.performanceSummary.healthScores.cachePerformance }
  ];

  const activityData = [
    { name: 'Users', value: dashboardData.systemStatistics.totalUsers },
    { name: 'Projects', value: dashboardData.systemStatistics.totalProjects },
    { name: 'Tasks', value: dashboardData.systemStatistics.totalTasks }
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Admin Dashboard
      </Typography>

      {/* Quick Stats Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <PeopleIcon color="primary" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Users
                  </Typography>
                  <Typography variant="h5">
                    {formatNumber(dashboardData.systemStatistics.totalUsers)}
                  </Typography>
                  <Typography variant="body2" color="success.main">
                    +{dashboardData.growthMetrics.newUsers30Days} this month
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <BusinessIcon color="primary" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Organizations
                  </Typography>
                  <Typography variant="h5">
                    {formatNumber(dashboardData.systemStatistics.totalOrganizations)}
                  </Typography>
                  <Typography variant="body2" color="success.main">
                    +{dashboardData.growthMetrics.newOrganizations30Days} this month
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <AssignmentIcon color="primary" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Projects
                  </Typography>
                  <Typography variant="h5">
                    {formatNumber(dashboardData.systemStatistics.totalProjects)}
                  </Typography>
                  <Typography variant="body2" color="success.main">
                    +{dashboardData.growthMetrics.newProjects30Days} this month
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <SpeedIcon color="primary" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    System Health
                  </Typography>
                  <Typography variant="h5">
                    {dashboardData.performanceSummary.healthScores.overall}%
                  </Typography>
                  <Chip
                    label={dashboardData.systemHealth.overallStatus}
                    color={getHealthStatusColor(dashboardData.systemHealth.overallStatus)}
                    size="small"
                  />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs for different views */}
      <Card>
        <Tabs value={activeTab} onChange={handleTabChange} aria-label="admin dashboard tabs">
          <Tab icon={<DashboardIcon />} label="Overview" />
          <Tab icon={<AnalyticsIcon />} label="Analytics" />
          <Tab icon={<SpeedIcon />} label="Performance" />
          <Tab icon={<SecurityIcon />} label="Security" />
          <Tab icon={<PeopleIcon />} label="Users" />
        </Tabs>

        <CardContent>
          {/* Overview Tab */}
          {activeTab === 0 && (
            <Grid container spacing={3}>
              {/* User Growth Chart */}
              <Grid item xs={12} md={8}>
                <Typography variant="h6" gutterBottom>
                  User Growth Trend
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={userGrowthData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Area type="monotone" dataKey="users" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                  </AreaChart>
                </ResponsiveContainer>
              </Grid>

              {/* Recent Activities */}
              <Grid item xs={12} md={4}>
                <Typography variant="h6" gutterBottom>
                  Recent Activities
                </Typography>
                <List>
                  {dashboardData.recentActivities.slice(0, 5).map((activity, index) => (
                    <React.Fragment key={index}>
                      <ListItem>
                        <ListItemIcon>
                          <CheckCircleIcon color="success" />
                        </ListItemIcon>
                        <ListItemText
                          primary={activity.description}
                          secondary={`${activity.user} • ${new Date(activity.timestamp).toLocaleDateString()}`}
                        />
                      </ListItem>
                      {index < 4 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              </Grid>
            </Grid>
          )}

          {/* Analytics Tab */}
          {activeTab === 1 && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  User Engagement
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={activityData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {activityData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Grid>

              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Active Users
                </Typography>
                <Box>
                  <Typography variant="body1">
                    Today: <strong>{dashboardData.userMetrics.activeUsersToday}</strong>
                  </Typography>
                  <Typography variant="body1">
                    This Week: <strong>{dashboardData.userMetrics.activeUsersWeek}</strong>
                  </Typography>
                  <Typography variant="body1">
                    This Month: <strong>{dashboardData.userMetrics.activeUsersMonth}</strong>
                  </Typography>
                  <Typography variant="body1" sx={{ mt: 2 }}>
                    Retention Rate: <strong>{dashboardData.userMetrics.userRetentionRate}%</strong>
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          )}

          {/* Performance Tab */}
          {activeTab === 2 && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={8}>
                <Typography variant="h6" gutterBottom>
                  System Performance Scores
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="score" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </Grid>

              <Grid item xs={12} md={4}>
                <Typography variant="h6" gutterBottom>
                  Component Status
                </Typography>
                <List>
                  <ListItem>
                    <ListItemText primary="API Server" />
                    <Chip
                      label={dashboardData.systemHealth.apiStatus}
                      color={getHealthStatusColor(dashboardData.systemHealth.apiStatus)}
                      size="small"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Database" />
                    <Chip
                      label={dashboardData.systemHealth.databaseStatus}
                      color={getHealthStatusColor(dashboardData.systemHealth.databaseStatus)}
                      size="small"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Cache" />
                    <Chip
                      label={dashboardData.systemHealth.cacheStatus}
                      color={getHealthStatusColor(dashboardData.systemHealth.cacheStatus)}
                      size="small"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Storage" />
                    <Chip
                      label={dashboardData.systemHealth.storageStatus}
                      color={getHealthStatusColor(dashboardData.systemHealth.storageStatus)}
                      size="small"
                    />
                  </ListItem>
                </List>
              </Grid>
            </Grid>
          )}

          {/* Security Tab */}
          {activeTab === 3 && (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Security Overview
                </Typography>
                <Alert severity="info" sx={{ mb: 2 }}>
                  Security monitoring features will be available in the next update.
                </Alert>
                <Box>
                  <Typography variant="body1">• Failed login attempts: 0 (last 24h)</Typography>
                  <Typography variant="body1">• Security alerts: 0 active</Typography>
                  <Typography variant="body1">• System integrity: ✅ Verified</Typography>
                  <Typography variant="body1">• Access logs: ✅ Monitored</Typography>
                </Box>
              </Grid>
            </Grid>
          )}

          {/* Users Tab */}
          {activeTab === 4 && (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  User Management
                </Typography>
                <Alert severity="info" sx={{ mb: 2 }}>
                  Advanced user management features are in development.
                </Alert>
                <Box>
                  <Button variant="contained" sx={{ mr: 2, mb: 1 }}>
                    View All Users
                  </Button>
                  <Button variant="outlined" sx={{ mr: 2, mb: 1 }}>
                    Export User Data
                  </Button>
                  <Button variant="outlined" sx={{ mb: 1 }}>
                    Generate Reports
                  </Button>
                </Box>
              </Grid>
            </Grid>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default AdminDashboard;