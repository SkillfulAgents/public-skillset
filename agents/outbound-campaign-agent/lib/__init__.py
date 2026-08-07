"""Vendor-neutral outbound machinery.

  config    load and resolve the team's config file
  adapters  the vendor seam: sourcing / enrichment / sender / crm / calendar /
            suppression / notify
  db        SQLite state and the decision audit log
  identity  name splitting, match verification, personal-domain policy
  icp       config-driven qualification
  linter    mechanical enforcement of copy standards
  caps      send-cap governor and deliverability kill switches
"""
__all__ = ["config", "adapters", "db", "identity", "icp", "linter", "caps"]
