import '../../widgets/state_view_widget.dart';
import 'stats_view.dart';

class Stats extends StateView<StatsState> {
  Stats({super.key})
      : super(
          stateBuilder: (context) => StatsState(context),
          view: StatsView(),
        );
}

class StatsState extends StateProvider<Stats> {
  StatsState(super.context);
}
