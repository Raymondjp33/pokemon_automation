import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../components/bordered_box.dart';
import '../../../services/file_provider.dart';

// Maps display label → serial command string (matches common.py press() commands)
const _buttons = [
  ('A', 'A'),
  ('B', 'B'),
  ('X', 'X'),
  ('Y', 'Y'),
  ('L', 'L'),
  ('R', 'R'),
  ('ZL', 'ZL'),
  ('ZR', 'ZR'),
  ('+', '+'),
  ('-', '-'),
  ('↑', 'w'),
  ('↓', 's'),
  ('←', 'a'),
  ('→', 'd'),
  ('Home', 'H'),
  ('Cap', 'C'),
];

class SwitchControllerWidget extends StatefulWidget {
  const SwitchControllerWidget({required this.switchNum, super.key});

  final int switchNum;

  @override
  State<SwitchControllerWidget> createState() => _SwitchControllerWidgetState();
}

class _SwitchControllerWidgetState extends State<SwitchControllerWidget> {
  bool _enabled = false;
  String? _lastResult;

  @override
  void didUpdateWidget(SwitchControllerWidget old) {
    super.didUpdateWidget(old);
    // Disable controller whenever the active switch changes
    if (old.switchNum != widget.switchNum) {
      _enabled = false;
      _lastResult = null;
    }
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<FileProvider>();
    final scriptRunning = provider.scripts.any((s) => s.running);

    // Controller is only usable when enabled AND no script is running
    final canControl = _enabled && !scriptRunning;

    return BorderedBox(
      width: 480,
      padding: const EdgeInsets.all(10),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text(
                'Controller',
                style: TextStyle(
                  color: Colors.white,
                  fontFamily: 'Minecraft',
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              if (scriptRunning)
                const Padding(
                  padding: EdgeInsets.only(right: 10),
                  child: Text(
                    '⚠ script running',
                    style: TextStyle(color: Colors.orange, fontSize: 10),
                  ),
                ),
              // Enable toggle
              GestureDetector(
                onTap: scriptRunning
                    ? null
                    : () => setState(() {
                          _enabled = !_enabled;
                          _lastResult = null;
                        }),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 150),
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
                  decoration: BoxDecoration(
                    color: canControl
                        ? Colors.greenAccent.withValues(alpha: 0.15)
                        : scriptRunning
                            ? Colors.grey.shade900
                            : const Color(0xFF1E2A4A),
                    border: Border.all(
                      color: canControl
                          ? Colors.greenAccent
                          : scriptRunning
                              ? Colors.grey.shade700
                              : const Color(0xFF4C6CBF),
                    ),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    canControl ? 'Enabled' : 'Enable',
                    style: TextStyle(
                      color: canControl
                          ? Colors.greenAccent
                          : scriptRunning
                              ? Colors.grey
                              : Colors.white70,
                      fontSize: 11,
                      fontFamily: 'Minecraft',
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: [
              for (final (label, cmd) in _buttons)
                _ButtonPad(
                  label: label,
                  active: canControl,
                  onPressed: canControl
                      ? () {
                          provider.sendButton(widget.switchNum, cmd);
                          setState(() => _lastResult = label);
                        }
                      : null,
                ),
            ],
          ),
          if (_lastResult != null && canControl) ...[
            const SizedBox(height: 6),
            Text(
              'Sent: $_lastResult',
              style: const TextStyle(color: Colors.greenAccent, fontSize: 10),
            ),
          ],
        ],
      ),
    );
  }
}

class _ButtonPad extends StatelessWidget {
  const _ButtonPad({
    required this.label,
    required this.active,
    required this.onPressed,
  });

  final String label;
  final bool active;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 44,
      height: 36,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor:
              active ? const Color(0xFF1E2A4A) : const Color(0xFF111827),
          disabledBackgroundColor: const Color(0xFF111827),
          padding: EdgeInsets.zero,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(4),
            side: BorderSide(
              color: active
                  ? const Color(0xFF4C6CBF)
                  : const Color(0xFF2A2A3A),
            ),
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: active ? Colors.white : Colors.white24,
            fontSize: 10,
            fontFamily: 'Minecraft',
          ),
        ),
      ),
    );
  }
}
