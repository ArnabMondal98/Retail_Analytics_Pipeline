import React, { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Progress } from "../components/ui/progress";
import { toast } from "sonner";
import { 
  PlayCircle, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Loader2,
  Database,
  Sparkles,
  BarChart3,
  Users,
  LineChart,
  FileText,
  Upload,
  FileSpreadsheet,
  AlertCircle,
  Check
} from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const STAGES = [
  { id: 'ingestion', label: 'Data Ingestion', icon: Database, description: 'Load and validate data' },
  { id: 'cleaning', label: 'Data Cleaning', icon: Sparkles, description: 'Remove duplicates, handle nulls' },
  { id: 'feature_engineering', label: 'Feature Engineering', icon: Sparkles, description: 'Create derived features' },
  { id: 'eda', label: 'Exploratory Analysis', icon: BarChart3, description: 'Generate insights' },
  { id: 'rfm_analysis', label: 'RFM Analysis', icon: Users, description: 'Customer segmentation by RFM' },
  { id: 'segmentation', label: 'K-Means Clustering', icon: Users, description: 'Machine learning segmentation' },
  { id: 'clv', label: 'CLV Calculation', icon: LineChart, description: 'Customer lifetime value' },
  { id: 'kpi_generation', label: 'KPI Generation', icon: BarChart3, description: 'Calculate key metrics' },
  { id: 'performance_analysis', label: 'Performance Analysis', icon: BarChart3, description: 'Monthly & category analysis' },
  { id: 'forecasting', label: 'Sales Forecasting', icon: LineChart, description: 'Predict future sales' },
  { id: 'report_generation', label: 'Report Generation', icon: FileText, description: 'Create HTML reports' },
  { id: 'export', label: 'Data Export', icon: FileText, description: 'Export to CSV/Excel' },
];

const StageItem = ({ stage, status, isActive }) => {
  const Icon = stage.icon;
  
  const getStatusIcon = () => {
    if (status === 'completed') return <CheckCircle2 className="w-5 h-5 text-green-500" />;
    if (status === 'failed') return <XCircle className="w-5 h-5 text-red-500" />;
    if (isActive) return <Loader2 className="w-5 h-5 text-[#2563EB] animate-spin" />;
    return <Clock className="w-5 h-5 text-muted-foreground" />;
  };

  const getBgColor = () => {
    if (status === 'completed') return 'bg-green-50 border-green-200';
    if (status === 'failed') return 'bg-red-50 border-red-200';
    if (isActive) return 'bg-blue-50 border-[#2563EB]';
    return 'bg-white border-border';
  };

  return (
    <div 
      className={`p-4 rounded-xl border-2 transition-all duration-300 ${getBgColor()}`}
      data-testid={`stage-${stage.id}`}
    >
      <div className="flex items-start gap-4">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
          status === 'completed' ? 'bg-green-100' :
          status === 'failed' ? 'bg-red-100' :
          isActive ? 'bg-[#2563EB]/10' : 'bg-muted'
        }`}>
          <Icon className={`w-5 h-5 ${
            status === 'completed' ? 'text-green-600' :
            status === 'failed' ? 'text-red-600' :
            isActive ? 'text-[#2563EB]' : 'text-muted-foreground'
          }`} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className="font-semibold text-[#0F172A]">{stage.label}</h4>
            {getStatusIcon()}
          </div>
          <p className="text-sm text-muted-foreground mt-1">{stage.description}</p>
        </div>
      </div>
    </div>
  );
};

const Pipeline = () => {
  const [status, setStatus] = useState({
    status: 'idle',
    progress: 0,
    current_stage: null,
    stages_completed: [],
    start_time: null,
    end_time: null,
    error: null
  });
  const [dataInfo, setDataInfo] = useState(null);
  const [datasets, setDatasets] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [pollingInterval, setPollingInterval] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    const init = async () => {
      setIsLoading(true);
      try {
        await Promise.all([
          fetchDataInfo(),
          fetchStatus(),
          fetchDatasets()
        ]);
      } finally {
        setIsLoading(false);
      }
    };
    init();
    
    return () => {
      if (pollingInterval) clearInterval(pollingInterval);
    };
  }, [fetchStatus, pollingInterval]);

  const fetchDataInfo = async () => {
    try {
      const res = await axios.get(`${API}/data/info`);
      console.log('Data info:', res.data);
      setDataInfo(res.data);
    } catch (err) {
      console.error("Error fetching data info:", err);
    }
  };

  const fetchDatasets = async () => {
    try {
      const res = await axios.get(`${API}/data/datasets`);
      console.log('Datasets:', res.data);
      setDatasets(res.data);
    } catch (err) {
      console.error("Error fetching datasets:", err);
    }
  };

  const fetchStatus = useCallback(async () => {
  try {
    const res = await axios.get(`${API}/pipeline/status`);
    setStatus(res.data);

    if (res.data.status === "running") {
      setIsRunning(true);
    } else {
      setIsRunning(false);
      if (pollingInterval) {
        clearInterval(pollingInterval);
        setPollingInterval(null);
      }
    }
  } catch (err) {
    console.error("Error fetching status:", err);
  }
}, [pollingInterval, otherDeps]);

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setIsUploading(true);
    
    try {
      const res = await axios.post(`${API}/data/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      toast.success(`Dataset uploaded: ${res.data.filename}`);
      fetchDataInfo();
      fetchDatasets();
    } catch (err) {
      console.error("Upload error:", err);
      toast.error(err.response?.data?.detail || "Upload failed");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const activateDataset = async (filename) => {
    try {
      await axios.post(`${API}/data/activate/${filename}`);
      toast.success(`Dataset '${filename}' activated`);
      fetchDataInfo();
      fetchDatasets();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Activation failed");
    }
  };

  const startPipeline = async () => {
    try {
      setIsRunning(true);
      await axios.post(`${API}/pipeline/run`);
      toast.success("Pipeline started successfully!");
      
      // Start polling for status updates
      const interval = setInterval(fetchStatus, 2000);
      setPollingInterval(interval);
      
    } catch (err) {
      console.error("Error starting pipeline:", err);
      toast.error(err.response?.data?.detail || "Failed to start pipeline");
      setIsRunning(false);
    }
  };

  const getStageStatus = (stageId) => {
    if (status.stages_completed.includes(stageId)) return 'completed';
    if (status.error && status.current_stage === stageId) return 'failed';
    return 'pending';
  };

  const isStageActive = (stageId) => {
    return status.current_stage === stageId && status.status === 'running';
  };

  const formatDuration = (start, end) => {
    if (!start) return '-';
    const startTime = new Date(start);
    const endTime = end ? new Date(end) : new Date();
    const diff = Math.floor((endTime - startTime) / 1000);
    
    if (diff < 60) return `${diff}s`;
    return `${Math.floor(diff / 60)}m ${diff % 60}s`;
  };

  return (
    <div className="space-y-8 animate-fade-in" data-testid="pipeline-page">
      {/* Dataset Upload Card */}
      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="w-5 h-5 text-[#2563EB]" />
            Upload Dataset
          </CardTitle>
          <CardDescription>
            Upload your retail transaction data (Excel or CSV)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Upload Area */}
            <div 
              className="border-2 border-dashed border-border rounded-xl p-8 text-center hover:border-[#2563EB] transition-colors cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".xlsx,.xls,.csv"
                onChange={handleFileUpload}
                className="hidden"
                data-testid="file-upload-input"
              />
              {isUploading ? (
                <div className="flex flex-col items-center gap-3">
                  <Loader2 className="w-12 h-12 text-[#2563EB] animate-spin" />
                  <p className="text-muted-foreground">Uploading and validating...</p>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-3">
                  <FileSpreadsheet className="w-12 h-12 text-muted-foreground" />
                  <div>
                    <p className="font-medium text-[#0F172A]">Click to upload or drag and drop</p>
                    <p className="text-sm text-muted-foreground mt-1">
                      Supports .xlsx, .xls, .csv files
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Required Columns Info */}
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-[#2563EB] mt-0.5" />
                <div>
                  <p className="font-medium text-[#0F172A]">Required columns:</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    transaction_id, quantity, transaction_date, price, customer_id, transaction_amount
                  </p>
                </div>
              </div>
            </div>

            {/* Available Datasets */}
            {datasets.length > 0 && (
              <div className="space-y-2">
                <p className="text-sm font-medium text-muted-foreground">Available Datasets:</p>
                <div className="space-y-2">
                  {datasets.map((dataset, index) => (
                    <div 
                      key={index}
                      className={`flex items-center justify-between p-3 rounded-lg border ${
                        dataset.is_active ? 'border-[#2563EB] bg-blue-50' : 'border-border'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <FileSpreadsheet className="w-5 h-5 text-muted-foreground" />
                        <div>
                          <p className="font-medium text-[#0F172A]">{dataset.filename}</p>
                          <p className="text-xs text-muted-foreground">{dataset.size_mb} MB</p>
                        </div>
                      </div>
                      {dataset.is_active ? (
                        <Badge className="bg-[#2563EB]">
                          <Check className="w-3 h-3 mr-1" />
                          Active
                        </Badge>
                      ) : (
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => activateDataset(dataset.filename)}
                        >
                          Activate
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Data Info Card */}
      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="w-5 h-5 text-[#2563EB]" />
            Active Dataset
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="w-4 h-4 animate-spin" />
              Loading dataset info...
            </div>
          ) : dataInfo && dataInfo.exists ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div>
                <p className="text-sm text-muted-foreground">File</p>
                <p className="font-semibold text-[#0F172A]">{dataInfo.filename}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Size</p>
                <p className="font-semibold text-[#0F172A]">{dataInfo.size_mb} MB</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Rows</p>
                <p className="font-semibold text-[#0F172A]">{dataInfo.rows?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Columns</p>
                <p className="font-semibold text-[#0F172A]">{dataInfo.columns}</p>
              </div>
            </div>
          ) : (
            <p className="text-muted-foreground">No dataset loaded. Upload a dataset to begin.</p>
          )}
        </CardContent>
      </Card>

      {/* Pipeline Control */}
      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Pipeline Execution</CardTitle>
              <CardDescription>Run the complete analytics pipeline</CardDescription>
            </div>
            <Button
              onClick={startPipeline}
              disabled={isRunning || status.status === 'running' || !dataInfo?.exists}
              className="bg-[#2563EB] hover:bg-[#1D4ED8]"
              data-testid="run-pipeline-btn"
            >
              {isRunning || status.status === 'running' ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <PlayCircle className="w-4 h-4 mr-2" />
                  Run Pipeline
                </>
              )}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Status Bar */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <Badge variant={
                  status.status === 'completed' ? 'default' :
                  status.status === 'failed' ? 'destructive' :
                  status.status === 'running' ? 'secondary' : 'outline'
                }>
                  {status.status.toUpperCase()}
                </Badge>
                {status.current_stage && (
                  <span className="text-muted-foreground">
                    Current: {STAGES.find(s => s.id === status.current_stage)?.label}
                  </span>
                )}
              </div>
              <span className="font-medium">{Math.round(status.progress)}%</span>
            </div>
            <Progress value={status.progress} className="h-2" />
          </div>

          {/* Timing Info */}
          {status.start_time && (
            <div className="flex items-center gap-6 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                <span>Duration: {formatDuration(status.start_time, status.end_time)}</span>
              </div>
              <div>
                Stages: {status.stages_completed.length}/{STAGES.length}
              </div>
            </div>
          )}

          {/* Error Display */}
          {status.error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <XCircle className="w-5 h-5 text-red-500 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-red-700">Pipeline Error</h4>
                  <p className="text-sm text-red-600 mt-1">{status.error}</p>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pipeline Stages */}
      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <CardTitle>Pipeline Stages</CardTitle>
          <CardDescription>12-step automated analytics workflow</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {STAGES.map((stage, index) => (
              <StageItem
                key={stage.id}
                stage={stage}
                status={getStageStatus(stage.id)}
                isActive={isStageActive(stage.id)}
              />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Pipeline;
