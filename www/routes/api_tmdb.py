"""
disk2iso - TMDB API Routes
Stellt TMDB-spezifische API-Endpoints bereit
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from flask import Blueprint, jsonify
from datetime import datetime

# Blueprint für TMDB API
api_tmdb_bp = Blueprint('api_tmdb', __name__)

INSTALL_DIR = Path("/opt/disk2iso")
TMDB_LIB = Path("/opt/disk2iso-tmdb/lib/libtmdb.sh")

@api_tmdb_bp.route('/api/metadata/tmdb/pending')
def api_tmdb_pending():
    """
    Prüft ob TMDB-Metadaten-Auswahl ansteht
    
    Ruft tmdb_get_cached_queries() aus libtmdb.sh auf.
    Diese Bash-Funktion:
    - Sucht nach *.tmdbquery Dateien
    - Berechnet Timeout
    - Parst TMDB-Suchergebnisse
    - Gibt strukturiertes JSON zurück
    
    Returns:
        {
            'pending': bool,
            'disc_type': 'dvd-video' | 'bd-video',
            'disc_id': str,
            'timeout': int (seconds remaining),
            'results': [...]
        }
    """
    try:
        # Prüfe ob TMDB-Modul installiert ist
        if not TMDB_LIB.exists():
            return jsonify({
                'pending': False,
                'error': 'TMDB module not installed'
            })
        
        # Rufe Bash-Funktion auf
        script = f"""
        source {INSTALL_DIR}/lib/liblogging.sh
        source {INSTALL_DIR}/lib/libfolders.sh
        source {INSTALL_DIR}/lib/libsettings.sh
        source {TMDB_LIB}
        tmdb_get_cached_queries
        """
        
        result = subprocess.run(
            ['/bin/bash', '-c', script],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout.strip():
            # Parse JSON von Bash
            data = json.loads(result.stdout)
            return jsonify(data)
        else:
            # Keine pending queries
            return jsonify({'pending': False})
            
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error in tmdb_get_cached_queries: {e}", file=sys.stderr)
        return jsonify({
            'pending': False,
            'error': 'Invalid JSON from bash function'
        }), 500
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'pending': False,
            'error': 'Timeout calling bash function'
        }), 500
        
    except Exception as e:
        print(f"Error in api_tmdb_pending: {e}", file=sys.stderr)
        return jsonify({
            'pending': False,
            'error': str(e)
        }), 500

@api_tmdb_bp.route('/api/metadata/tmdb/select', methods=['POST'])
def api_tmdb_select():
    """
    Verarbeitet TMDB-Auswahl des Benutzers
    
    Ruft tmdb_parse_selection() aus libtmdb.sh auf.
    Diese Bash-Funktion:
    - Liest .tmdbquery Datei
    - Extrahiert ausgewählten Movie/TV-Show
    - Schreibt Metadaten in DISC_INFO/DISC_DATA Arrays via metadata_set_data()
    - Aktualisiert disc_label
    
    Body:
        {
            'disc_id': str,
            'index': int (oder 'skip' für Überspringen)
        }
    
    Returns:
        {'success': bool, 'disc_id': str, 'index': int}
    """
    try:
        data = request.get_json()
        
        if not data or 'disc_id' not in data:
            return jsonify({'success': False, 'message': 'disc_id missing'}), 400
        
        disc_id = data['disc_id']
        index = data.get('index', 'skip')
        
        # Skip-Handling
        if index == 'skip':
            return jsonify({
                'success': True,
                'disc_id': disc_id,
                'index': -1,
                'skipped': True
            })
        
        # Hole output_dir aus Settings
        output_dir = _get_output_dir()
        
        # Finde .tmdbquery Datei
        query_file = Path(output_dir) / f"{disc_id}_tmdb.tmdbquery"
        
        if not query_file.exists():
            return jsonify({
                'success': False,
                'message': f'Query file not found: {query_file}'
            }), 404
        
        # Rufe tmdb_parse_selection() auf
        # Parameter: selected_index, query_file, select_file (nicht verwendet)
        script = f"""
        source {INSTALL_DIR}/lib/liblogging.sh
        source {INSTALL_DIR}/lib/libdiskinfos.sh
        source {INSTALL_DIR}/lib/libfolders.sh
        source {INSTALL_DIR}/lib/libsettings.sh
        source {INSTALL_DIR}-metadata/lib/libmetadata.sh
        source {TMDB_LIB}
        
        # Initialisiere DISC_INFO/DISC_DATA Arrays
        declare -gA DISC_INFO
        declare -gA DISC_DATA
        
        # Parse Selection und schreibe in Arrays
        tmdb_parse_selection {index} "{query_file}" ""
        """
        
        result = subprocess.run(
            ['/bin/bash', '-c', script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'disc_id': disc_id,
                'index': index
            })
        else:
            error_msg = result.stderr.strip() if result.stderr else 'Unknown error'
            print(f"tmdb_parse_selection failed: {error_msg}", file=sys.stderr)
            return jsonify({
                'success': False,
                'message': f'Parse failed: {error_msg}'
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Timeout calling bash function'
        }), 500
        
    except Exception as e:
        print(f"Error in api_tmdb_select: {e}", file=sys.stderr)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

def _get_output_dir():
    """Liest output_dir aus Settings (via libsettings.sh)"""
    try:
        script = f"""
        source {INSTALL_DIR}/lib/libsettings.sh
        settings_get_value_conf "disk2iso" "DEFAULT_OUTPUT_DIR" "/media/iso"
        """
        result = subprocess.run(
            ['/bin/bash', '-c', script],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return "/media/iso"
    except Exception:
        return "/media/iso"
