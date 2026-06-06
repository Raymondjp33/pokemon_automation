import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../components/bordered_box.dart';
import '../../../models/script_info.model.dart';
import '../../../services/file_provider.dart';

class ScriptManagerWidget extends StatefulWidget {
  const ScriptManagerWidget({required this.switchNum, super.key});

  final int switchNum;

  @override
  State<ScriptManagerWidget> createState() => _ScriptManagerWidgetState();
}

class _ScriptManagerWidgetState extends State<ScriptManagerWidget> {
  String? _selected;
  int _startingBox = 1;

  @override
  void didUpdateWidget(ScriptManagerWidget old) {
    super.didUpdateWidget(old);
    // If the selected script no longer exists in the list, clear it
  }

  ScriptInfo? _selectedInfo(List<ScriptInfo> scripts) =>
      _selected == null ? null : scripts.where((s) => s.name == _selected).firstOrNull;

  List<DropdownMenuItem<String>> _buildItems(List<ScriptInfo> scripts) {
    final Map<String, List<ScriptInfo>> grouped = {};
    for (final s in scripts) {
      grouped.putIfAbsent(s.category, () => []).add(s);
    }

    final items = <DropdownMenuItem<String>>[];
    for (final entry in grouped.entries) {
      // Category header — disabled, not selectable
      items.add(
        DropdownMenuItem<String>(
          enabled: false,
          value: '__${entry.key}',
          child: Text(
            entry.key.toUpperCase(),
            style: const TextStyle(
              color: Color(0xFF4C6CBF),
              fontSize: 11,
              fontFamily: 'Minecraft',
              letterSpacing: 1.2,
            ),
          ),
        ),
      );
      for (final s in entry.value) {
        items.add(
          DropdownMenuItem<String>(
            value: s.name,
            child: Row(
              children: [
                Container(
                  width: 7,
                  height: 7,
                  margin: const EdgeInsets.only(right: 8),
                  decoration: BoxDecoration(
                    color: s.running ? Colors.greenAccent : Colors.grey,
                    shape: BoxShape.circle,
                  ),
                ),
                Text(
                  s.name,
                  style: const TextStyle(color: Colors.white, fontSize: 11),
                ),
                const SizedBox(width: 8),
                Text(
                  s.description,
                  style: const TextStyle(color: Colors.white54, fontSize: 10),
                ),
              ],
            ),
          ),
        );
      }
    }
    return items;
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<FileProvider>();
    final scripts = provider.scripts;
    final running = scripts.where((s) => s.running).toList();
    final info = _selectedInfo(scripts);
    final switchNum = widget.switchNum;

    return BorderedBox(
      width: 480,
      padding: const EdgeInsets.all(10),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Script Manager',
            style: TextStyle(
              color: Colors.white,
              fontFamily: 'Minecraft',
              fontSize: 14,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 10),

          // Running scripts
          const Text(
            'RUNNING',
            style: TextStyle(
              color: Color(0xFF4C6CBF),
              fontFamily: 'Minecraft',
              fontSize: 11,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 4),
          if (running.isEmpty)
            const Text(
              'None',
              style: TextStyle(color: Colors.white38, fontSize: 11),
            )
          else
            for (final s in running)
              Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Row(
                  children: [
                    Container(
                      width: 7,
                      height: 7,
                      margin: const EdgeInsets.only(right: 8),
                      decoration: const BoxDecoration(
                        color: Colors.greenAccent,
                        shape: BoxShape.circle,
                      ),
                    ),
                    Text(
                      s.name,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 11,
                        fontFamily: 'Minecraft',
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      s.description,
                      style: const TextStyle(color: Colors.white54, fontSize: 10),
                    ),
                    const Spacer(),
                    SizedBox(
                      width: 48,
                      height: 22,
                      child: ElevatedButton(
                        onPressed: () => provider.stopScript(s.name),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.red.shade700,
                          padding: EdgeInsets.zero,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(4),
                          ),
                        ),
                        child: const Text(
                          'Stop',
                          style: TextStyle(fontSize: 10, color: Colors.white),
                        ),
                      ),
                    ),
                  ],
                ),
              ),

          const SizedBox(height: 12),

          // Launch section
          const Text(
            'LAUNCH',
            style: TextStyle(
              color: Color(0xFF4C6CBF),
              fontFamily: 'Minecraft',
              fontSize: 11,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 6),

          if (scripts.isEmpty)
            const Text(
              'Connecting...',
              style: TextStyle(color: Colors.grey, fontSize: 11),
            )
          else
            Row(
              children: [
                // Script dropdown
                Expanded(
                  child: Container(
                    height: 28,
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                    decoration: BoxDecoration(
                      color: const Color(0xFF1E2A4A),
                      border: Border.all(color: const Color(0xFF4C6CBF)),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: DropdownButtonHideUnderline(
                      child: DropdownButton<String>(
                        value: _selected,
                        hint: const Text(
                          'Select script...',
                          style: TextStyle(color: Colors.white38, fontSize: 11),
                        ),
                        isDense: true,
                        style: const TextStyle(color: Colors.white, fontSize: 11),
                        dropdownColor: const Color(0xFF1E2A4A),
                        isExpanded: true,
                        items: _buildItems(scripts),
                        onChanged: (v) {
                          if (v != null && !v.startsWith('__')) {
                            setState(() => _selected = v);
                          }
                        },
                      ),
                    ),
                  ),
                ),

                // Starting box picker (home:sort only)
                if (info?.needsStartingBox == true) ...[
                  const SizedBox(width: 6),
                  _SmallDropdown<int>(
                    value: _startingBox,
                    items: List.generate(30, (i) => i + 1),
                    label: (v) => 'Bx$v',
                    onChanged: (v) => setState(() => _startingBox = v),
                  ),
                ],

                const SizedBox(width: 6),

                // Start button
                SizedBox(
                  width: 56,
                  height: 28,
                  child: ElevatedButton(
                    onPressed: info == null || info.running
                        ? null
                        : () => provider.startScript(
                              info.name,
                              switchNum: info.needsSwitchNum ? switchNum : null,
                              startingBox: info.needsStartingBox ? _startingBox : null,
                            ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF4C6CBF),
                      disabledBackgroundColor: Colors.grey.shade800,
                      padding: EdgeInsets.zero,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(4),
                      ),
                    ),
                    child: Text(
                      info?.running == true ? 'Running' : 'Start',
                      style: const TextStyle(fontSize: 10, color: Colors.white),
                    ),
                  ),
                ),
              ],
            ),

          // Description line for selected script
          if (info != null) ...[
            const SizedBox(height: 4),
            Text(
              info.argsHint.isNotEmpty
                  ? '${info.description}  ·  ${info.argsHint}'
                  : info.description,
              style: const TextStyle(color: Colors.white38, fontSize: 10),
            ),
          ],
        ],
      ),
    );
  }
}

class _SmallDropdown<T> extends StatelessWidget {
  const _SmallDropdown({
    required this.value,
    required this.items,
    required this.label,
    required this.onChanged,
  });

  final T value;
  final List<T> items;
  final String Function(T) label;
  final ValueChanged<T> onChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 28,
      padding: const EdgeInsets.symmetric(horizontal: 6),
      decoration: BoxDecoration(
        color: const Color(0xFF1E2A4A),
        border: Border.all(color: const Color(0xFF4C6CBF)),
        borderRadius: BorderRadius.circular(4),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<T>(
          value: value,
          isDense: true,
          style: const TextStyle(color: Colors.white, fontSize: 10),
          dropdownColor: const Color(0xFF1E2A4A),
          items: items
              .map(
                (i) => DropdownMenuItem<T>(
                  value: i,
                  child: Text(label(i)),
                ),
              )
              .toList(),
          onChanged: (v) {
            if (v != null) onChanged(v);
          },
        ),
      ),
    );
  }
}
