#!/usr/bin/env python3
"""
Secure SSH Tools for KnowledgePersistence-AI
Scriptable SSH operations with key-based authentication
No password exposure in logs or commands
"""

import paramiko
import subprocess
import sys
import time
from pathlib import Path

class SecureSSHClient:
    """Secure SSH client with key-based authentication"""
    
    def __init__(self, hostname="192.168.10.90", username="greg", key_file="~/.ssh/id_ed25519_pgdbsrv"):
        self.hostname = hostname
        self.username = username
        self.key_file = Path(key_file).expanduser()
        self.client = None
        
    def connect(self):
        """Connect using SSH key authentication"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Use SSH key authentication
            self.client.connect(
                hostname=self.hostname,
                username=self.username,
                key_filename=str(self.key_file),
                timeout=10
            )
            return True
        except Exception as e:
            print(f"SSH connection failed: {e}")
            return False
    
    def execute(self, command, timeout=30):
        """Execute command on remote server"""
        if not self.client:
            if not self.connect():
                return None, "Connection failed"
        
        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
            
            # Wait for command to complete
            exit_status = stdout.channel.recv_exit_status()
            
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            
            return output, error if error else None
            
        except Exception as e:
            return None, f"Command execution failed: {e}"
    
    def execute_sudo(self, command, timeout=30):
        """Execute sudo command (assumes passwordless sudo is configured)"""
        return self.execute(f"sudo {command}", timeout)
    
    def copy_file(self, local_path, remote_path):
        """Copy file to remote server using SFTP"""
        if not self.client:
            if not self.connect():
                return False
        
        try:
            sftp = self.client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            return True
        except Exception as e:
            print(f"File copy failed: {e}")
            return False
    
    def close(self):
        """Close SSH connection"""
        if self.client:
            self.client.close()

class KnowledgePersistenceTools:
    """High-level tools for KnowledgePersistence-AI operations"""
    
    def __init__(self):
        self.ssh = SecureSSHClient()
    
    def check_database_status(self):
        """Check PostgreSQL database status"""
        output, error = self.ssh.execute_sudo("systemctl status postgresql")
        if error:
            return False, error
        
        return "active" in output.lower(), output
    
    def check_api_status(self):
        """Check API server status"""
        output, error = self.ssh.execute("curl -s http://localhost:8090/health")
        if error:
            return False, error
        
        return "healthy" in output, output
    
    def get_knowledge_count(self):
        """Get count of knowledge items"""
        cmd = "cd KnowledgePersistence-AI && source venv/bin/activate && python3 -c \"import os; import psycopg; conn = psycopg.connect(host='localhost', dbname='knowledge_persistence', user='postgres', password=os.getenv('DB_PASSWORD', '')); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM knowledge_items'); print(cur.fetchone()[0]); conn.close()\""
        
        output, error = self.ssh.execute(cmd)
        if error:
            return None, error
        
        try:
            return int(output.strip()), None
        except ValueError:
            return None, f"Invalid response: {output}"
    
    def sync_files(self, file_patterns=None):
        """Sync files to server"""
        if file_patterns is None:
            file_patterns = ["cag_*.py", "complete_session_storage.py", "redirection_analysis_tools.py", "test_*.py"]
        
        synced_files = []
        for pattern in file_patterns:
            # Use local rsync over SSH for efficiency
            cmd = f"rsync -avz -e 'ssh -i ~/.ssh/id_ed25519_pgdbsrv' {pattern} greg@192.168.10.90:/home/greg/KnowledgePersistence-AI/"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                synced_files.append(pattern)
            else:
                print(f"Sync failed for {pattern}: {result.stderr}")
        
        return synced_files
    
    def test_cag_performance(self):
        """Test CAG performance remotely"""
        cmd = """cd KnowledgePersistence-AI && source venv/bin/activate && timeout 30s python3 -c "
from cag_mcp_integrated import CAGEngineMCP
import asyncio
import time

async def test():
    engine = CAGEngineMCP()
    start = time.time()
    result = await engine.process_query('Performance test', 'perf-test', {'keywords': ['test']})
    duration = time.time() - start
    print(f'SUCCESS: {duration:.3f}s response time')
    print(f'Cache hit: {result[\\\"performance\\\"][\\\"cache_hit\\\"]}')
    print(f'Context tokens: {result[\\\"context_size_tokens\\\"]}')
    return True

try:
    asyncio.run(test())
except Exception as e:
    print(f'ERROR: {e}')
    exit(1)
\""""
        
        output, error = self.ssh.execute(cmd, timeout=60)
        return output, error
    
    def close(self):
        """Close connections"""
        self.ssh.close()

def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("Usage: python3 secure_ssh_tools.py <command>")
        print("Commands:")
        print("  status       - Check database and API status")
        print("  count        - Get knowledge items count")
        print("  sync         - Sync files to server")
        print("  test-cag     - Test CAG performance")
        print("  shell        - Interactive SSH shell")
        return
    
    command = sys.argv[1]
    tools = KnowledgePersistenceTools()
    
    try:
        if command == "status":
            db_status, db_output = tools.check_database_status()
            api_status, api_output = tools.check_api_status()
            
            print(f"Database: {'✅ Active' if db_status else '❌ Inactive'}")
            print(f"API: {'✅ Healthy' if api_status else '❌ Unhealthy'}")
            
        elif command == "count":
            count, error = tools.get_knowledge_count()
            if error:
                print(f"❌ Error: {error}")
            else:
                print(f"Knowledge items: {count}")
                
        elif command == "sync":
            synced = tools.sync_files()
            print(f"✅ Synced {len(synced)} file patterns")
            
        elif command == "test-cag":
            output, error = tools.test_cag_performance()
            if error:
                print(f"❌ Error: {error}")
            else:
                print(output)
                
        elif command == "shell":
            # Simple interactive shell
            ssh = SecureSSHClient()
            if ssh.connect():
                print("Connected to pgdbsrv. Type 'exit' to quit.")
                while True:
                    cmd = input("pgdbsrv$ ")
                    if cmd.lower() in ['exit', 'quit']:
                        break
                    output, error = ssh.execute(cmd)
                    if output:
                        print(output)
                    if error:
                        print(f"Error: {error}")
                ssh.close()
            else:
                print("❌ Connection failed")
                
        else:
            print(f"Unknown command: {command}")
            
    finally:
        tools.close()

if __name__ == "__main__":
    main()