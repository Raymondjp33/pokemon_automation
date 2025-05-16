import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class StateView<T extends StateProvider> extends StatefulWidget {
  final T Function(BuildContext) stateBuilder;
  final Widget view;
  StateView({super.key, required this.stateBuilder, required this.view}) {
    assert(
      T.toString() != 'StateProvider<StatefulWidget>',
      'Must specify a type.  '
      'Eg. class HomePage extends StateView<HomeState> {}  '
      'instead of class HomePage extends StateView {}',
    );
  }

  @override
  State<StateView<T>> createState() => _StateViewState<T>();
}

class _StateViewState<T extends StateProvider> extends State<StateView<T>> {
  T? state;

  @override
  Widget build(BuildContext context) {
    state?.dependenciesDidChange();
    return ChangeNotifierProvider<T>(
      create: (context) {
        state = widget.stateBuilder(context);
        return state!;
      },
      lazy: false,
      child: widget.view,
    );
  }
}

abstract class StateProvider<W extends StatefulWidget> extends ChangeNotifier {
  final BuildContext context;
  late W widget;
  void Function()? onDependenciesChanged;
  StateProvider(this.context, {this.onDependenciesChanged}) : super() {
    _updateWidgetReference();
    return;
  }
  void dependenciesDidChange() {
    _updateWidgetReference();
    onDependenciesChanged?.call();
    return;
  }

  void _updateWidgetReference() {
    W? ancestor = context.findAncestorWidgetOfExactType<W>();
    if (ancestor == null) {
      throw Exception(
        'No ancestor of type $W found for $runtimeType\n'
        'Make sure that you are following the pattern of StateProvider<Page, Event>()\n'
        'And not using StateProvider<View, Event>()',
      );
    }
    widget = ancestor;
    return;
  }

  bool get mounted => _mounted;
  bool _mounted = true;

  @override
  void dispose() {
    _mounted = false;
    super.dispose();
    return;
  }

  @override
  void notifyListeners() {
    if (mounted) {
      super.notifyListeners();
    }
    return;
  }
}
