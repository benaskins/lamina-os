{{/*
Expand the name of the chart.
*/}}
{{- define "lamina.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "lamina.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "lamina.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "lamina.labels" -}}
helm.sh/chart: {{ include "lamina.chart" . }}
{{ include "lamina.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
lamina.environment: {{ .Values.global.environment }}
lamina.sigil: {{ .Values.global.sigil }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "lamina.selectorLabels" -}}
app.kubernetes.io/name: {{ include "lamina.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
