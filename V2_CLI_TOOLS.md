# V2 Command Line Tools & Automation

## CLI Administration Interface

### System Management CLI

```python
#!/usr/bin/env python3
"""
KnowledgePersistence-AI V2 Command Line Administration Tool
Provides comprehensive system management capabilities
"""

import click
import asyncio
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from v2_admin_tools import (
    SystemHealthAnalyzer,
    PatternQualityAnalyzer,
    LearningEffectivenessAnalyzer,
    AdministrationDashboard,
    SystemConfigurationManager,
    PatternManagementTools
)

@click.group()
@click.version_option()
def cli():
    """KnowledgePersistence-AI V2 Administration CLI"""
    pass

@cli.group()
def system():
    """System management commands"""
    pass

@system.command()
@click.option('--days', default=7, help='Analysis period in days')
@click.option('--format', default='json', type=click.Choice(['json', 'table', 'summary']))
@click.option('--output', help='Output file path')
def health(days, format, output):
    """Generate system health report"""
    click.echo(f"Analyzing system health for the last {days} days...")
    
    async def run_health_analysis():
        health_analyzer = SystemHealthAnalyzer()
        health_report = await health_analyzer.generate_system_health_report(days)
        
        if format == 'json':
            result = json.dumps(health_report, indent=2, default=str)
        elif format == 'table':
            result = format_health_report_table(health_report)
        else:  # summary
            result = format_health_report_summary(health_report)
        
        if output:
            with open(output, 'w') as f:
                f.write(result)
            click.echo(f"Health report written to {output}")
        else:
            click.echo(result)
    
    asyncio.run(run_health_analysis())

@system.command()
@click.option('--metric', help='Specific metric to display')
@click.option('--days', default=30, help='Analysis period in days')
def performance(metric, days):
    """Display system performance metrics"""
    click.echo(f"Analyzing performance metrics for the last {days} days...")
    
    async def run_performance_analysis():
        dashboard = AdministrationDashboard()
        
        if metric:
            result = await dashboard.get_specific_metric(metric, days)
            click.echo(f"{metric}: {result}")
        else:
            kpis = await dashboard.calculate_key_performance_indicators()
            
            click.echo("Key Performance Indicators:")
            click.echo("-" * 40)
            for kpi_name, kpi_value in kpis.items():
                click.echo(f"{kpi_name.replace('_', ' ').title()}: {kpi_value:.3f}")
    
    asyncio.run(run_performance_analysis())

@cli.group()
def patterns():
    """Pattern management commands"""
    pass

@patterns.command()
@click.option('--quality-threshold', default=0.7, help='Minimum quality threshold')
@click.option('--usage-threshold', default=1, help='Minimum usage threshold')
@click.option('--dry-run', is_flag=True, help='Show what would be done without executing')
def curate(quality_threshold, usage_threshold, dry_run):
    """Curate patterns based on quality and usage"""
    click.echo(f"Curating patterns (quality >= {quality_threshold}, usage >= {usage_threshold})...")
    
    async def run_pattern_curation():
        pattern_tools = PatternManagementTools()
        
        curation_criteria = {
            'min_quality_score': quality_threshold,
            'min_usage_count': usage_threshold,
            'max_age_days': 365,
            'remove_duplicates': True,
            'merge_similar': True
        }
        
        curation_results = await pattern_tools.curate_patterns(curation_criteria)
        
        click.echo("Curation Results:")
        click.echo("-" * 20)
        click.echo(f"Patterns to keep: {len(curation_results['patterns_to_keep'])}")
        click.echo(f"Patterns to archive: {len(curation_results['patterns_to_archive'])}")
        click.echo(f"Patterns to delete: {len(curation_results['patterns_to_delete'])}")
        click.echo(f"Patterns to merge: {len(curation_results['patterns_to_merge'])}")
        
        if not dry_run:
            if click.confirm("Execute curation actions?"):
                await pattern_tools.execute_curation_actions(curation_results)
                click.echo("Curation completed successfully")
        else:
            click.echo("Dry run - no actions executed")
    
    asyncio.run(run_pattern_curation())

@patterns.command()
@click.option('--pattern-type', help='Filter by pattern type')
@click.option('--min-quality', default=0.0, help='Minimum quality score')
def validate(pattern_type, min_quality):
    """Validate pattern quality"""
    click.echo("Validating pattern quality...")
    
    async def run_pattern_validation():
        pattern_tools = PatternManagementTools()
        
        if pattern_type:
            patterns = await pattern_tools.get_patterns_by_type(pattern_type)
        else:
            patterns = await pattern_tools.get_all_patterns()
        
        validation_results = await pattern_tools.validate_pattern_quality(patterns)
        
        click.echo("Pattern Quality Validation Results:")
        click.echo("-" * 40)
        
        for quality_level, pattern_list in validation_results.items():
            if len(pattern_list) > 0:
                click.echo(f"{quality_level.replace('_', ' ').title()}: {len(pattern_list)}")
                
                if quality_level == 'invalid_patterns':
                    click.echo("  Invalid patterns:")
                    for pattern_info in pattern_list:
                        click.echo(f"    - {pattern_info['pattern'].title} (score: {pattern_info['quality_score']:.3f})")
    
    asyncio.run(run_pattern_validation())

@cli.group()
def learning():
    """Learning system management commands"""
    pass

@learning.command()
@click.option('--days', default=30, help='Analysis period in days')
@click.option('--detailed', is_flag=True, help='Show detailed analysis')
def analyze(days, detailed):
    """Analyze learning effectiveness"""
    click.echo(f"Analyzing learning effectiveness for the last {days} days...")
    
    async def run_learning_analysis():
        learning_analyzer = LearningEffectivenessAnalyzer()
        learning_analysis = await learning_analyzer.evaluate_learning(days)
        
        click.echo("Learning Effectiveness Analysis:")
        click.echo("-" * 40)
        
        metrics = learning_analysis['learning_metrics']
        
        click.echo(f"Learning Rate: {metrics['learning_rate']['current_rate']:.3f}")
        click.echo(f"Pattern Discovery Rate: {metrics['pattern_discovery_rate']:.3f}")
        click.echo(f"Strategy Improvement Rate: {metrics['strategy_improvement_rate']:.3f}")
        click.echo(f"Adaptation Effectiveness: {metrics['adaptation_effectiveness']['adaptation_success_rate']:.3f}")
        
        if detailed:
            click.echo("\nDetailed Analysis:")
            click.echo("-" * 20)
            
            for bottleneck in learning_analysis['learning_bottlenecks']:
                click.echo(f"Bottleneck: {bottleneck['type']}")
                click.echo(f"  Impact: {bottleneck['impact']}")
                click.echo(f"  Suggestion: {bottleneck['suggestion']}")
    
    asyncio.run(run_learning_analysis())

@learning.command()
@click.option('--learning-rate', type=float, help='Target learning rate')
@click.option('--adaptation-threshold', type=float, help='Adaptation threshold')
@click.option('--dry-run', is_flag=True, help='Show what would be optimized')
def optimize(learning_rate, adaptation_threshold, dry_run):
    """Optimize learning parameters"""
    click.echo("Optimizing learning parameters...")
    
    async def run_learning_optimization():
        config_manager = SystemConfigurationManager()
        
        optimization_config = {}
        if learning_rate:
            optimization_config['learning_rate'] = learning_rate
        if adaptation_threshold:
            optimization_config['adaptation_threshold'] = adaptation_threshold
        
        if not optimization_config:
            # Auto-optimize based on current performance
            recommendations = await config_manager.optimize_system_configuration()
            click.echo("Auto-optimization recommendations:")
            for rec in recommendations['recommendations']:
                click.echo(f"  - {rec['description']}")
                click.echo(f"    Impact: {rec['expected_impact']}")
        else:
            if dry_run:
                click.echo("Would apply the following optimizations:")
                for key, value in optimization_config.items():
                    click.echo(f"  - {key}: {value}")
            else:
                result = await config_manager.update_system_configuration(
                    optimization_config, "cli_user"
                )
                
                if result['success']:
                    click.echo("Learning parameters optimized successfully")
                else:
                    click.echo(f"Optimization failed: {result['error']}")
    
    asyncio.run(run_learning_optimization())

@cli.group()
def maintenance():
    """System maintenance commands"""
    pass

@maintenance.command()
@click.option('--vacuum', is_flag=True, help='Vacuum database')
@click.option('--reindex', is_flag=True, help='Reindex database')
@click.option('--cleanup-cache', is_flag=True, help='Clean up cache')
@click.option('--archive-old', is_flag=True, help='Archive old data')
def cleanup(vacuum, reindex, cleanup_cache, archive_old):
    """Perform system maintenance tasks"""
    click.echo("Performing system maintenance...")
    
    async def run_maintenance():
        maintenance_tasks = []
        
        if vacuum:
            maintenance_tasks.append(('vacuum_database', 'Vacuum database'))
        if reindex:
            maintenance_tasks.append(('reindex_database', 'Reindex database'))
        if cleanup_cache:
            maintenance_tasks.append(('cleanup_cache', 'Clean up cache'))
        if archive_old:
            maintenance_tasks.append(('archive_old_data', 'Archive old data'))
        
        if not maintenance_tasks:
            # Run all maintenance tasks
            maintenance_tasks = [
                ('vacuum_database', 'Vacuum database'),
                ('cleanup_cache', 'Clean up cache'),
                ('archive_old_data', 'Archive old data')
            ]
        
        for task_name, task_description in maintenance_tasks:
            click.echo(f"Running: {task_description}")
            
            # Execute maintenance task
            result = await execute_maintenance_task(task_name)
            
            if result['success']:
                click.echo(f"  ✓ {task_description} completed")
            else:
                click.echo(f"  ✗ {task_description} failed: {result['error']}")
    
    asyncio.run(run_maintenance())

@maintenance.command()
@click.option('--backup-path', required=True, help='Backup file path')
@click.option('--compress', is_flag=True, help='Compress backup')
@click.option('--include-patterns', is_flag=True, help='Include patterns in backup')
@click.option('--include-sessions', is_flag=True, help='Include sessions in backup')
def backup(backup_path, compress, include_patterns, include_sessions):
    """Create system backup"""
    click.echo(f"Creating system backup at {backup_path}...")
    
    async def run_backup():
        backup_config = {
            'backup_path': backup_path,
            'compress': compress,
            'include_patterns': include_patterns,
            'include_sessions': include_sessions,
            'timestamp': datetime.now().isoformat()
        }
        
        result = await execute_backup(backup_config)
        
        if result['success']:
            click.echo(f"Backup created successfully")
            click.echo(f"  Size: {result['backup_size']}")
            click.echo(f"  Duration: {result['backup_duration']}")
        else:
            click.echo(f"Backup failed: {result['error']}")
    
    asyncio.run(run_backup())

@cli.group()
def monitoring():
    """System monitoring commands"""
    pass

@monitoring.command()
@click.option('--interval', default=60, help='Monitoring interval in seconds')
@click.option('--metrics', multiple=True, help='Specific metrics to monitor')
def watch(interval, metrics):
    """Watch system metrics in real-time"""
    click.echo(f"Monitoring system metrics (interval: {interval}s)...")
    
    async def run_monitoring():
        dashboard = AdministrationDashboard()
        
        try:
            while True:
                # Clear screen
                click.clear()
                
                # Display timestamp
                click.echo(f"KnowledgePersistence-AI V2 Monitoring - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                click.echo("=" * 60)
                
                # Get current metrics
                if metrics:
                    for metric in metrics:
                        value = await dashboard.get_current_metric(metric)
                        click.echo(f"{metric}: {value}")
                else:
                    # Display all key metrics
                    kpis = await dashboard.calculate_key_performance_indicators()
                    
                    for kpi_name, kpi_value in kpis.items():
                        click.echo(f"{kpi_name.replace('_', ' ').title()}: {kpi_value:.3f}")
                
                # Display system alerts
                alerts = await dashboard.get_current_alerts()
                if alerts:
                    click.echo("\nActive Alerts:")
                    click.echo("-" * 20)
                    for alert in alerts:
                        click.echo(f"  {alert['severity'].upper()}: {alert['message']}")
                
                # Wait for next iteration
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            click.echo("\nMonitoring stopped")
    
    asyncio.run(run_monitoring())

@monitoring.command()
@click.option('--days', default=7, help='Report period in days')
@click.option('--format', default='summary', type=click.Choice(['summary', 'detailed', 'json']))
def report(days, format):
    """Generate monitoring report"""
    click.echo(f"Generating monitoring report for the last {days} days...")
    
    async def run_monitoring_report():
        dashboard = AdministrationDashboard()
        
        if format == 'detailed':
            report_data = await dashboard.generate_technical_dashboard()
        else:
            report_data = await dashboard.generate_executive_dashboard()
        
        if format == 'json':
            click.echo(json.dumps(report_data, indent=2, default=str))
        else:
            # Format as readable report
            click.echo("System Monitoring Report")
            click.echo("=" * 30)
            click.echo(f"Report Period: {days} days")
            click.echo(f"Generated: {report_data['timestamp']}")
            click.echo(f"System Health Score: {report_data['system_health_score']:.3f}")
            
            if 'kpis' in report_data:
                click.echo("\nKey Performance Indicators:")
                click.echo("-" * 30)
                for kpi_name, kpi_value in report_data['kpis'].items():
                    click.echo(f"{kpi_name.replace('_', ' ').title()}: {kpi_value:.3f}")
            
            if 'recommendations' in report_data:
                click.echo("\nRecommendations:")
                click.echo("-" * 15)
                for rec in report_data['recommendations']:
                    click.echo(f"  - {rec['description']}")
    
    asyncio.run(run_monitoring_report())

# Utility functions
def format_health_report_table(health_report):
    """Format health report as table"""
    from tabulate import tabulate
    
    table_data = []
    for category, data in health_report.items():
        if isinstance(data, dict):
            for key, value in data.items():
                table_data.append([category, key, value])
        else:
            table_data.append([category, '', data])
    
    return tabulate(table_data, headers=['Category', 'Metric', 'Value'])

def format_health_report_summary(health_report):
    """Format health report as summary"""
    summary = []
    summary.append(f"System Health Score: {health_report['system_overview']['overall_health_score']:.3f}")
    summary.append(f"Analysis Period: {health_report['system_overview']['analysis_period']} days")
    summary.append(f"Total Sessions: {health_report['system_overview']['total_sessions']}")
    summary.append(f"Total Interactions: {health_report['system_overview']['total_interactions']}")
    
    if health_report['system_overview']['critical_issues']:
        summary.append("\nCritical Issues:")
        for issue in health_report['system_overview']['critical_issues']:
            summary.append(f"  - {issue['description']}")
    
    return '\n'.join(summary)

async def execute_maintenance_task(task_name):
    """Execute specific maintenance task"""
    # Implementation would depend on specific maintenance requirements
    pass

async def execute_backup(backup_config):
    """Execute system backup"""
    # Implementation would depend on specific backup requirements
    pass

if __name__ == '__main__':
    cli()
```

### Automated Analysis Scripts

```python
#!/usr/bin/env python3
"""
Automated Analysis Scripts for KnowledgePersistence-AI V2
Runs scheduled analysis and optimization tasks
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List

class AutomatedAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('automated_analysis.log'),
                logging.StreamHandler()
            ]
        )
    
    async def run_daily_analysis(self):
        """Run daily system analysis"""
        self.logger.info("Starting daily system analysis")
        
        try:
            # System health check
            health_report = await self.analyze_system_health()
            
            # Pattern quality analysis
            pattern_analysis = await self.analyze_pattern_quality()
            
            # Learning effectiveness analysis
            learning_analysis = await self.analyze_learning_effectiveness()
            
            # Generate summary report
            daily_report = {
                'timestamp': datetime.now().isoformat(),
                'analysis_type': 'daily',
                'system_health': health_report,
                'pattern_quality': pattern_analysis,
                'learning_effectiveness': learning_analysis,
                'recommendations': await self.generate_daily_recommendations(
                    health_report, pattern_analysis, learning_analysis
                )
            }
            
            # Save report
            await self.save_analysis_report(daily_report)
            
            # Check for critical issues
            await self.check_for_critical_issues(daily_report)
            
            self.logger.info("Daily system analysis completed successfully")
            
        except Exception as e:
            self.logger.error(f"Daily analysis failed: {str(e)}")
            await self.send_alert(f"Daily analysis failed: {str(e)}")
    
    async def run_weekly_optimization(self):
        """Run weekly system optimization"""
        self.logger.info("Starting weekly system optimization")
        
        try:
            # Analyze performance trends
            performance_trends = await self.analyze_performance_trends(days=7)
            
            # Identify optimization opportunities
            optimization_opportunities = await self.identify_optimization_opportunities()
            
            # Execute safe optimizations
            optimization_results = await self.execute_safe_optimizations(
                optimization_opportunities
            )
            
            # Pattern curation
            curation_results = await self.run_pattern_curation()
            
            # Generate optimization report
            weekly_report = {
                'timestamp': datetime.now().isoformat(),
                'analysis_type': 'weekly_optimization',
                'performance_trends': performance_trends,
                'optimization_opportunities': optimization_opportunities,
                'optimization_results': optimization_results,
                'curation_results': curation_results,
                'recommendations': await self.generate_weekly_recommendations(
                    performance_trends, optimization_results
                )
            }
            
            # Save report
            await self.save_analysis_report(weekly_report)
            
            self.logger.info("Weekly system optimization completed successfully")
            
        except Exception as e:
            self.logger.error(f"Weekly optimization failed: {str(e)}")
            await self.send_alert(f"Weekly optimization failed: {str(e)}")
    
    async def run_monthly_deep_analysis(self):
        """Run monthly deep system analysis"""
        self.logger.info("Starting monthly deep system analysis")
        
        try:
            # Comprehensive pattern analysis
            pattern_deep_analysis = await self.run_deep_pattern_analysis()
            
            # Learning system evolution analysis
            learning_evolution = await self.analyze_learning_evolution()
            
            # Long-term trend analysis
            long_term_trends = await self.analyze_long_term_trends()
            
            # System architecture recommendations
            architecture_recommendations = await self.generate_architecture_recommendations()
            
            # Generate comprehensive report
            monthly_report = {
                'timestamp': datetime.now().isoformat(),
                'analysis_type': 'monthly_deep_analysis',
                'pattern_deep_analysis': pattern_deep_analysis,
                'learning_evolution': learning_evolution,
                'long_term_trends': long_term_trends,
                'architecture_recommendations': architecture_recommendations,
                'executive_summary': await self.generate_executive_summary(
                    pattern_deep_analysis, learning_evolution, long_term_trends
                )
            }
            
            # Save report
            await self.save_analysis_report(monthly_report)
            
            self.logger.info("Monthly deep system analysis completed successfully")
            
        except Exception as e:
            self.logger.error(f"Monthly deep analysis failed: {str(e)}")
            await self.send_alert(f"Monthly deep analysis failed: {str(e)}")
    
    async def check_for_critical_issues(self, analysis_report):
        """Check for critical issues requiring immediate attention"""
        critical_issues = []
        
        # Check system health
        if analysis_report['system_health']['overall_health_score'] < 0.7:
            critical_issues.append({
                'type': 'system_health',
                'severity': 'critical',
                'description': 'System health score below critical threshold',
                'value': analysis_report['system_health']['overall_health_score']
            })
        
        # Check pattern quality
        if analysis_report['pattern_quality']['overall_quality_score'] < 0.6:
            critical_issues.append({
                'type': 'pattern_quality',
                'severity': 'high',
                'description': 'Pattern quality degradation detected',
                'value': analysis_report['pattern_quality']['overall_quality_score']
            })
        
        # Check learning effectiveness
        if analysis_report['learning_effectiveness']['learning_rate']['current_rate'] < 0.1:
            critical_issues.append({
                'type': 'learning_stagnation',
                'severity': 'medium',
                'description': 'Learning rate below acceptable threshold',
                'value': analysis_report['learning_effectiveness']['learning_rate']['current_rate']
            })
        
        # Send alerts for critical issues
        if critical_issues:
            await self.send_critical_alerts(critical_issues)
    
    async def send_critical_alerts(self, critical_issues):
        """Send alerts for critical issues"""
        alert_message = "Critical Issues Detected:\n"
        
        for issue in critical_issues:
            alert_message += f"- {issue['severity'].upper()}: {issue['description']}\n"
            alert_message += f"  Current Value: {issue['value']}\n"
        
        self.logger.critical(alert_message)
        
        # Send email/notification (implementation depends on notification system)
        await self.send_alert(alert_message)
    
    async def save_analysis_report(self, report):
        """Save analysis report to database and file"""
        # Save to database
        await self.save_report_to_database(report)
        
        # Save to file
        filename = f"analysis_report_{report['analysis_type']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.logger.info(f"Analysis report saved: {filename}")

# Scheduler for automated tasks
class AnalysisScheduler:
    def __init__(self):
        self.analyzer = AutomatedAnalyzer()
        self.running = False
        
    async def start_scheduler(self):
        """Start the analysis scheduler"""
        self.running = True
        
        # Schedule daily analysis at 2 AM
        daily_task = asyncio.create_task(self.schedule_daily_analysis())
        
        # Schedule weekly optimization on Sundays at 3 AM
        weekly_task = asyncio.create_task(self.schedule_weekly_optimization())
        
        # Schedule monthly deep analysis on the 1st of each month at 1 AM
        monthly_task = asyncio.create_task(self.schedule_monthly_analysis())
        
        await asyncio.gather(daily_task, weekly_task, monthly_task)
    
    async def schedule_daily_analysis(self):
        """Schedule daily analysis"""
        while self.running:
            now = datetime.now()
            next_run = now.replace(hour=2, minute=0, second=0, microsecond=0)
            
            if next_run <= now:
                next_run += timedelta(days=1)
            
            wait_seconds = (next_run - now).total_seconds()
            await asyncio.sleep(wait_seconds)
            
            if self.running:
                await self.analyzer.run_daily_analysis()
    
    async def schedule_weekly_optimization(self):
        """Schedule weekly optimization"""
        while self.running:
            now = datetime.now()
            days_ahead = 6 - now.weekday()  # Sunday is 6
            
            if days_ahead <= 0:
                days_ahead += 7
            
            next_run = now.replace(hour=3, minute=0, second=0, microsecond=0) + timedelta(days=days_ahead)
            
            wait_seconds = (next_run - now).total_seconds()
            await asyncio.sleep(wait_seconds)
            
            if self.running:
                await self.analyzer.run_weekly_optimization()
    
    async def schedule_monthly_analysis(self):
        """Schedule monthly analysis"""
        while self.running:
            now = datetime.now()
            
            # Next first day of month at 1 AM
            if now.day == 1 and now.hour < 1:
                next_run = now.replace(hour=1, minute=0, second=0, microsecond=0)
            else:
                next_month = now.replace(day=28) + timedelta(days=4)
                next_run = next_month.replace(day=1, hour=1, minute=0, second=0, microsecond=0)
            
            wait_seconds = (next_run - now).total_seconds()
            await asyncio.sleep(wait_seconds)
            
            if self.running:
                await self.analyzer.run_monthly_deep_analysis()

if __name__ == '__main__':
    scheduler = AnalysisScheduler()
    asyncio.run(scheduler.start_scheduler())
```

This comprehensive CLI and automation suite provides professional-grade administration capabilities for your adaptive intelligence system. The tools recognize that you're building a sophisticated learning system that requires proper management, monitoring, and optimization tooling.

