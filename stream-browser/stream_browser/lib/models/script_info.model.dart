class ScriptInfo {
  final String name;
  final String description;
  final String argsHint;
  final bool running;
  final int? pid;
  final String? started;

  const ScriptInfo({
    required this.name,
    required this.description,
    required this.argsHint,
    required this.running,
    this.pid,
    this.started,
  });

  factory ScriptInfo.fromJson(Map<String, dynamic> json) => ScriptInfo(
        name: json['name'] as String,
        description: json['description'] as String,
        argsHint: json['args_hint'] as String? ?? '',
        running: json['running'] as bool,
        pid: json['pid'] as int?,
        started: json['started'] as String?,
      );

  bool get needsSwitchNum => argsHint.contains('switch_num');
  bool get needsStartingBox => argsHint.contains('starting_box');

  String get category {
    if (!name.contains(':')) return 'tools';
    return name.split(':').first;
  }
}
