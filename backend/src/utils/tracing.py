"""Cloud Trace logging utilities."""

import json
import logging
from typing import Any

import google.cloud.storage as storage
from google.cloud import logging as google_cloud_logging


class CloudTraceLoggingSpanExporter:
    """Extended CloudTraceSpanExporter with Cloud Logging and GCS support."""

    def __init__(
        self,
        project_id: str,
        logging_client: google_cloud_logging.Client | None = None,
        storage_client: storage.Client | None = None,
        bucket_name: str | None = None,
        service_name: str = "adk-agent",
        debug: bool = False,
    ) -> None:
        """Initialize the exporter.

        Args:
            project_id: Google Cloud project ID
            logging_client: Google Cloud Logging client
            storage_client: Google Cloud Storage client
            bucket_name: GCS bucket for large payloads
            service_name: Service name for logging
            debug: Enable debug mode
        """
        self.project_id = project_id
        self.debug = debug
        self.service_name = service_name
        self.logging_client = logging_client or google_cloud_logging.Client(
            project=self.project_id
        )
        self.logger = self.logging_client.logger(__name__)
        self.storage_client = storage_client or storage.Client(
            project=self.project_id
        )
        self.bucket_name = (
            bucket_name or f"{self.project_id}-agent-logs-data"
        )
        self.bucket = self.storage_client.bucket(self.bucket_name)

    def export(self, spans: Any) -> None:
        """Export spans to Cloud Logging.

        Args:
            spans: Sequence of spans to export
        """
        for span in spans:
            try:
                span_context = span.get_span_context()
                if span_context is None:
                    continue
                trace_id = format(span_context.trace_id, "x")
                span_id = format(span_context.span_id, "x")
                span_dict = json.loads(span.to_json())

                span_dict["trace"] = (
                    f"projects/{self.project_id}/traces/{trace_id}"
                )
                span_dict["span_id"] = span_id

                span_dict = self._process_large_attributes(
                    span_dict=span_dict, span_id=span_id
                )

                if self.debug:
                    print(span_dict)

                self.logger.log_struct(
                    span_dict,
                    labels={
                        "type": "agent_telemetry",
                        "service_name": self.service_name,
                    },
                    severity="INFO",
                )
            except Exception as e:
                logging.error(f"Error exporting span: {e}")

    def store_in_gcs(self, content: str, span_id: str) -> str:
        """Store large content in GCS.

        Args:
            content: Content to store
            span_id: Span ID

        Returns:
            GCS URI of stored content
        """
        if not self.storage_client.bucket(self.bucket_name).exists():
            logging.warning(
                f"Bucket {self.bucket_name} not found. "
                "Unable to store span attributes in GCS."
            )
            return "GCS bucket not found"

        blob_name = f"spans/{span_id}.json"
        blob = self.bucket.blob(blob_name)

        blob.upload_from_string(content, "application/json")
        return f"gs://{self.bucket_name}/{blob_name}"

    def _process_large_attributes(
        self, span_dict: dict, span_id: str
    ) -> dict:
        """Process large attributes by storing in GCS if needed.

        Args:
            span_dict: Span data dictionary
            span_id: Span ID

        Returns:
            Updated span dictionary
        """
        attributes = span_dict["attributes"]
        if len(json.dumps(attributes).encode()) > 255 * 1024:
            attributes_payload = dict(attributes.items())
            attributes_retain = dict(attributes.items())

            gcs_uri = self.store_in_gcs(
                json.dumps(attributes_payload), span_id
            )
            attributes_retain["uri_payload"] = gcs_uri
            attributes_retain["url_payload"] = (
                f"https://storage.mtls.cloud.google.com/"
                f"{self.bucket_name}/spans/{span_id}.json"
            )

            span_dict["attributes"] = attributes_retain
            logging.info(
                "Payload above 250 KB, storing attributes in GCS"
            )

        return span_dict
