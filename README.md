# LiveFlow Open Core

This repository publishes the reusable recurrence engine in `open_core/` under the Mozilla Public License 2.0. The license applies to the files identified in `LICENSE` and the license map maintained by the publisher.

The Windows LiveFlow application is a separate, mixed-license product. Its desktop interface, database, OAuth and YouTube integration, private payment assets, and release configuration are not part of this source archive. The MPL license does not grant rights to those components, the LiveFlow name, or its artwork.

## Open Core module

`open_core/recurrence.py` generates daily, weekly, monthly, and interval-based occurrences, renders date templates, and serializes recurrence rules, including an optional time cutoff on the final date. The module uses the Python standard library.

Run its tests with:

```powershell
python -m unittest discover -s open_core/tests -v
```

## License and contributions

The published source files are covered by the Mozilla Public License 2.0 in `LICENSE`. See `CONTRIBUTING.md` before proposing a change. Security reports and support links are listed in `SECURITY.md` and `SUPPORT.md`.

This repository does not provide a Windows installer or a complete build of the LiveFlow desktop application.
