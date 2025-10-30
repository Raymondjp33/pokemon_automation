import 'package:json_annotation/json_annotation.dart';

part 'stats.model.g.dart';

@JsonSerializable(explicitToJson: true)
class StatsModel {
  int totalEggShinies;
  int totalEggs;
  double averageEggs;
  int totalStaticShinies;
  int totalStatic;
  double averageStatic;
  int totalWildShinies;
  int totalWild;
  double averageWild;

  StatsModel({
    this.totalEggShinies = 0,
    this.totalEggs = 0,
    this.averageEggs = 0,
    this.totalStaticShinies = 0,
    this.totalStatic = 0,
    this.averageStatic = 0,
    this.totalWildShinies = 0,
    this.totalWild = 0,
    this.averageWild = 0,
  });

  static StatsModel get emptyPokemon => StatsModel();

  factory StatsModel.fromJson(Map<String, dynamic>? json) {
    if (json == null) throw Exception('StatsModel: json was null');
    try {
      return _$StatsModelFromJson(json);
    } catch (e, stack) {
      throw 'StatsModel.fromJson: $e, $stack';
    }
  }

  Map<String, dynamic> toJson() {
    Map<String, dynamic> json = _$StatsModelToJson(this);
    return json;
  }
}
