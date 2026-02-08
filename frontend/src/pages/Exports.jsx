import React, { useState, useEffect } from "react";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Skeleton } from "../components/ui/skeleton";
import { toast } from "sonner";
import { 
  Download, 
  FileSpreadsheet, 
  FileText, 
  Clock, 
  HardDrive,
  Loader2,
  FileDown,
  RefreshCw
} from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const DATA_TYPES = [
  { value: 'cleaned', label: 'Cleaned Data', description: 'Full cleaned transaction dataset' },
  { value: 'rfm', label: 'RFM Analysis', description: 'Customer RFM scores and segments' },
  { value: 'segments', label: 'Customer Segments', description: 'K-Means cluster assignments' },
  { value: 'clv', label: 'Customer LTV', description: 'Customer lifetime value data' },
];

const FORMATS = [
  { value: 'csv', label: 'CSV', icon: FileText },
  { value: 'excel', label: 'Excel', icon: FileSpreadsheet },
];

const Exports = () => {
  const [exports, setExports] = useState([]);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [generatingReport, setGeneratingReport] = useState(false);
  const [selectedDataType, setSelectedDataType] = useState('cleaned');
  const [selectedFormat, setSelectedFormat] = useState('csv');

  useEffect(() => {
    fetchExports();
    fetchReports();
  }, []);

  const fetchExports = async () => {
    try {
      const res = await axios.get(`${API}/exports`);
      setExports(res.data);
    } catch (err) {
      console.error("Error fetching exports:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchReports = async () => {
    try {
      const res = await axios.get(`${API}/reports`);
      setReports(res.data);
    } catch (err) {
      console.error("Error fetching reports:", err);
    }
  };

  const generateExport = async () => {
    try {
      setGenerating(true);
      const res = await axios.post(`${API}/exports/generate`, {
        data_type: selectedDataType,
        format: selectedFormat
      });
      
      toast.success(`Export generated: ${res.data.filename}`);
      fetchExports();
    } catch (err) {
      console.error("Error generating export:", err);
      toast.error(err.response?.data?.detail || "Failed to generate export");
    } finally {
      setGenerating(false);
    }
  };

  const generateReport = async () => {
    try {
      setGeneratingReport(true);
      const res = await axios.post(`${API}/reports/generate`);
      
      toast.success(`Report generated: ${res.data.filename}`);
      fetchReports();
    } catch (err) {
      console.error("Error generating report:", err);
      toast.error(err.response?.data?.detail || "Failed to generate report");
    } finally {
      setGeneratingReport(false);
    }
  };

  const downloadFile = (filename) => {
    window.open(`${API}/exports/${filename}`, '_blank');
  };

  const formatFileSize = (kb) => {
    if (kb >= 1024) return `${(kb / 1024).toFixed(1)} MB`;
    return `${kb.toFixed(1)} KB`;
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleString();
  };

  const getFileIcon = (filename) => {
    if (filename.endsWith('.xlsx') || filename.endsWith('.xls')) {
      return <FileSpreadsheet className="w-5 h-5 text-green-600" />;
    }
    if (filename.endsWith('.html')) {
      return <FileText className="w-5 h-5 text-orange-600" />;
    }
    return <FileText className="w-5 h-5 text-blue-600" />;
  };

  return (
    <div className="space-y-8 animate-fade-in" data-testid="exports-page">
      {/* Generate Export Section */}
      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileDown className="w-5 h-5 text-[#2563EB]" />
            Generate Data Export
          </CardTitle>
          <CardDescription>Export processed datasets to CSV or Excel format</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Data Type Selection */}
            <div>
              <label className="text-sm font-medium text-muted-foreground mb-2 block">Data Type</label>
              <Select value={selectedDataType} onValueChange={setSelectedDataType}>
                <SelectTrigger data-testid="select-data-type">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {DATA_TYPES.map(type => (
                    <SelectItem key={type.value} value={type.value}>
                      <div>
                        <p className="font-medium">{type.label}</p>
                        <p className="text-xs text-muted-foreground">{type.description}</p>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Format Selection */}
            <div>
              <label className="text-sm font-medium text-muted-foreground mb-2 block">Format</label>
              <Select value={selectedFormat} onValueChange={setSelectedFormat}>
                <SelectTrigger data-testid="select-format">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {FORMATS.map(format => (
                    <SelectItem key={format.value} value={format.value}>
                      <div className="flex items-center gap-2">
                        <format.icon className="w-4 h-4" />
                        <span>{format.label}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Generate Button */}
            <div className="flex items-end">
              <Button 
                onClick={generateExport}
                disabled={generating}
                className="w-full bg-[#2563EB] hover:bg-[#1D4ED8]"
                data-testid="generate-export-btn"
              >
                {generating ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4 mr-2" />
                    Generate Export
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Generate Report Section */}
      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-orange-500" />
                Generate HTML Report
              </CardTitle>
              <CardDescription>Create a comprehensive analytics report</CardDescription>
            </div>
            <Button 
              onClick={generateReport}
              disabled={generatingReport}
              variant="outline"
              data-testid="generate-report-btn"
            >
              {generatingReport ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <FileText className="w-4 h-4 mr-2" />
                  Generate Report
                </>
              )}
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Available Files */}
      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Available Downloads</CardTitle>
              <CardDescription>Previously generated exports and reports</CardDescription>
            </div>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => { fetchExports(); fetchReports(); }}
              data-testid="refresh-exports-btn"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          ) : exports.length === 0 && reports.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <HardDrive className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No exports available yet</p>
              <p className="text-sm mt-1">Generate an export to see it here</p>
            </div>
          ) : (
            <div className="space-y-3">
              {/* Reports */}
              {reports.map((report, index) => (
                <div 
                  key={`report-${index}`}
                  className="flex items-center justify-between p-4 bg-orange-50 rounded-lg hover:bg-orange-100 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <FileText className="w-8 h-8 text-orange-600" />
                    <div>
                      <p className="font-medium text-[#0F172A]">{report.filename}</p>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground mt-1">
                        <span className="flex items-center gap-1">
                          <HardDrive className="w-3 h-3" />
                          {formatFileSize(report.size_kb)}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formatDate(report.created)}
                        </span>
                      </div>
                    </div>
                  </div>
                  <Button 
                    variant="outline"
                    size="sm"
                    onClick={() => downloadFile(report.filename)}
                    data-testid={`download-${report.filename}`}
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download
                  </Button>
                </div>
              ))}

              {/* Data Exports */}
              {exports.map((file, index) => (
                <div 
                  key={`export-${index}`}
                  className="flex items-center justify-between p-4 bg-muted/50 rounded-lg hover:bg-muted transition-colors"
                >
                  <div className="flex items-center gap-4">
                    {getFileIcon(file.filename)}
                    <div>
                      <p className="font-medium text-[#0F172A]">{file.filename}</p>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground mt-1">
                        <Badge variant="secondary">{file.type}</Badge>
                        <span className="flex items-center gap-1">
                          <HardDrive className="w-3 h-3" />
                          {formatFileSize(file.size_kb)}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formatDate(file.created)}
                        </span>
                      </div>
                    </div>
                  </div>
                  <Button 
                    variant="outline"
                    size="sm"
                    onClick={() => downloadFile(file.filename)}
                    data-testid={`download-${file.filename}`}
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Export Types Info */}
      <Card className="bg-white border-border shadow-sm">
        <CardHeader>
          <CardTitle>Available Export Types</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {DATA_TYPES.map(type => (
              <div key={type.value} className="p-4 border border-border rounded-lg">
                <h4 className="font-semibold text-[#0F172A]">{type.label}</h4>
                <p className="text-sm text-muted-foreground mt-1">{type.description}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Exports;
